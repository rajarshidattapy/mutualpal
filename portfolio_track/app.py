from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import json
import google.generativeai as genai
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch

# Initialize Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Gemini
genai.configure(api_key="apna API khud daal lund ke")

# Global variable to store current dataframe for chatbot queries
current_df = None
current_summary = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # --- Read and clean CSV ---
    try:
        df = pd.read_csv(filepath)
    except Exception:
        return "Invalid CSV format", 400

    df.columns = [c.strip().capitalize() for c in df.columns]
    if 'Description' not in df.columns or 'Debit' not in df.columns:
        return "CSV must contain 'Description' and 'Debit' columns.", 400

    # --- Categorization ---
    categories = {
        'Food': ['zomato', 'swiggy', 'restaurant', 'food', 'eat'],
        'Fuel': ['shell', 'petrol', 'fuel', 'indianoil', 'hpcl'],
        'Shopping': ['amazon', 'flipkart', 'myntra', 'shopping'],
        'Rent': ['rent', 'landlord'],
        'Bills': ['electricity', 'water', 'phone', 'wifi', 'bill'],
        'Groceries': ['bigbasket', 'mart', 'grocery', 'd-mart']
    }

    df['Category'] = 'Other'
    for cat, keywords in categories.items():
        for word in keywords:
            df.loc[df['Description'].str.contains(word, case=False, na=False), 'Category'] = cat

    summary = df.groupby('Category')['Debit'].sum().sort_values(ascending=False).to_dict()

    # Store globally for chatbot
    global current_df, current_summary
    current_df = df.copy()
    current_summary = summary

    # --- Monthly breakdown ---
    monthly_data = {}
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        if not df.empty:
            df['Month'] = df['Date'].dt.strftime('%Y-%m')
            df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
            
            # Group by month
            for month in df['Month'].unique():
                month_df = df[df['Month'] == month]
                monthly_data[month] = month_df[['Date_str', 'Description', 'Debit', 'Category']].to_dict('records')

    # --- Time-series and per-category-over-time ---
    timeseries = {}
    dates = []
    totals = []
    category_series = {}

    if 'Date' in df.columns:
        # parse dates and numeric debit
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        if not df.empty:
            df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d')
            df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)

            # overall daily totals
            daily = df.groupby('Date_str')['Debit'].sum().sort_index()
            timeseries = daily.to_dict()
            dates = list(daily.index)
            totals = list(daily.values)

            # per-category series aligned to dates
            pivot = df.pivot_table(index='Date_str', columns='Category', values='Debit', aggfunc='sum').reindex(dates).fillna(0)
            category_series = {str(col): pivot[col].tolist() for col in pivot.columns}

    # --- Ask Gemini for personalized advice ---
    summary_text = "\n".join([f"{k}: ₹{v:.2f}" for k, v in summary.items()])
    
    # Basic advice
    prompt = f"""
    The following is a user's monthly spending summary (in INR):
    {summary_text}

    Provide detailed, personalized financial advice to help them save money, improve budgeting, 
    and identify overspending categories. 
    
    Structure your response as follows:
    1. Start with a brief overview of their spending pattern
    2. Identify 3-4 key areas for improvement with specific recommendations
    3. Provide actionable tips for each category
    4. End with an encouraging summary
    
    Use clear formatting with line breaks between sections.
    Respond as a professional financial advisor.
    """

    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(prompt)
    advice = response.text if hasattr(response, 'text') else "Could not generate advice."
    
    # Format advice for better display
    advice = advice.replace('**', '<strong>').replace('**', '</strong>')
    advice = advice.replace('\n\n', '</p><p>').replace('\n', '<br>')
    if not advice.startswith('<p>'):
        advice = '<p>' + advice + '</p>'

    # Goal-based savings suggestion
    goal_prompt = f"""
    Based on this spending pattern:
    {summary_text}
    
    Create a detailed, structured plan to help the user save ₹10,000 per month.
    
    Format your response as:
    
    **Goal: Save ₹10,000/month**
    
    **Action Plan:**
    
    1. [Category] - [Specific Action]
       Current: ₹X | Target: ₹Y | Savings: ₹Z
       
    2. [Category] - [Specific Action]
       Current: ₹X | Target: ₹Y | Savings: ₹Z
    
    (Continue for 4-5 items)
    
    **Expected Monthly Savings: ₹10,000+**
    
    **Timeline:** Achievable in 2-3 months with consistent effort.
    
    Be specific with numbers and actionable steps.
    """
    goal_response = model.generate_content(goal_prompt)
    goal_plan = goal_response.text if hasattr(goal_response, 'text') else "Could not generate savings plan."
    
    # Format goal plan for better display
    goal_plan = goal_plan.replace('**', '<strong>').replace('**', '</strong>')
    goal_plan = goal_plan.replace('\n\n', '</p><p>').replace('\n', '<br>')
    if not goal_plan.startswith('<p>'):
        goal_plan = '<p>' + goal_plan + '</p>'

    # Micro-insights
    total_spending = sum(summary.values())
    discretionary = summary.get('Food', 0) + summary.get('Shopping', 0)
    discretionary_pct = (discretionary / total_spending * 100) if total_spending > 0 else 0
    
    micro_insights = []
    if discretionary_pct > 40:
        potential_savings = discretionary * 0.15
        micro_insights.append(f"💡 Your discretionary spending (Food + Shopping) is {discretionary_pct:.1f}% of total. Reducing to 30% could save ₹{potential_savings:.0f}/month.")
    
    if summary.get('Shopping', 0) > 10000:
        micro_insights.append(f"🛍️ You've spent ₹{summary.get('Shopping', 0):.0f} on shopping — consider setting a monthly budget.")
    
    if summary.get('Food', 0) > 8000:
        micro_insights.append(f"🍽️ Food spending is ₹{summary.get('Food', 0):.0f}. Try meal planning to reduce costs by 20-30%.")

    return render_template('result.html', 
                           summary=summary, 
                           advice=advice,
                           dates=dates, 
                           totals=totals, 
                           category_series=category_series,
                           monthly_data=monthly_data,
                           goal_plan=goal_plan,
                           micro_insights=micro_insights)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Handle natural language queries about spending"""
    global current_df, current_summary
    
    if current_df is None:
        return jsonify({"error": "No data loaded. Please upload a CSV first."}), 400
    
    query = request.json.get('query', '').lower()
    
    # Simple keyword-based query parsing
    if 'food' in query and 'spend' in query:
        food_total = current_summary.get('Food', 0)
        return jsonify({"response": f"You spent ₹{food_total:.2f} on food."})
    
    elif 'biggest' in query or 'highest' in query or 'most' in query:
        if current_summary:
            biggest = max(current_summary.items(), key=lambda x: x[1])
            return jsonify({"response": f"Your biggest expense is {biggest[0]} at ₹{biggest[1]:.2f}."})
    
    elif 'total' in query:
        total = sum(current_summary.values())
        return jsonify({"response": f"Your total spending is ₹{total:.2f}."})
    
    elif 'shopping' in query:
        shopping = current_summary.get('Shopping', 0)
        return jsonify({"response": f"You spent ₹{shopping:.2f} on shopping."})
    
    elif 'rent' in query:
        rent = current_summary.get('Rent', 0)
        return jsonify({"response": f"You spent ₹{rent:.2f} on rent."})
    
    elif 'bills' in query or 'utilities' in query:
        bills = current_summary.get('Bills', 0)
        return jsonify({"response": f"You spent ₹{bills:.2f} on bills and utilities."})
    
    else:
        # Use Gemini for more complex queries
        try:
            summary_text = "\n".join([f"{k}: ₹{v:.2f}" for k, v in current_summary.items()])
            prompt = f"""
            User spending summary:
            {summary_text}
            
            User question: {query}
            
            Provide a brief, helpful answer to their question about their spending.
            """
            model = genai.GenerativeModel("gemini-flash-latest")
            response = model.generate_content(prompt)
            answer = response.text if hasattr(response, 'text') else "I couldn't process that query."
            return jsonify({"response": answer})
        except Exception as e:
            return jsonify({"response": "Sorry, I couldn't understand that question. Try asking about 'food spending', 'biggest expense', or 'total spending'."})

@app.route('/download-pdf')
def download_pdf():
    """Generate and download PDF report"""
    global current_summary
    
    if current_summary is None:
        return "No data available", 400
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#007BFF'),
        spaceAfter=30,
        alignment=1
    )
    elements.append(Paragraph("Personal Financial Advisor Report", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary table
    elements.append(Paragraph("Spending Summary by Category", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    table_data = [['Category', 'Amount (₹)']]
    for cat, amount in current_summary.items():
        table_data.append([cat, f"₹{amount:.2f}"])
    
    total = sum(current_summary.values())
    table_data.append(['Total', f"₹{total:.2f}"])
    
    table = Table(table_data, colWidths=[3*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007BFF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f4ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='financial_report.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
