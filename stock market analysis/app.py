from flask import Flask, render_template, jsonify, request
from crewai import Agent, Task, Crew
from langchain_openrouter import ChatOpenRouter
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure OpenRouter
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Available models
MODELS = {
    "claude-3-opus": "anthropic/claude-3-opus-20240229",
    "claude-3-sonnet": "anthropic/claude-3-sonnet-20240229",
    "claude-2": "anthropic/claude-2",
    "gpt-4": "openai/gpt-4",
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
    "gemini-pro": "google/gemini-pro",
    "mixtral": "mistralai/mixtral-8x7b"
}

def get_llm(model_name):
    return ChatOpenRouter(
        api_key=OPENROUTER_API_KEY,
        model=MODELS[model_name],
        temperature=0.7
    )

def generate_response(prompt, model_name):
    llm = get_llm(model_name)
    response = llm.invoke(prompt)
    return response.content

# Define CrewAI Agents
def create_agents(model_name):
    data_analyst_agent = Agent(
        role="Data Analyst",
        goal="Monitor and analyze market data in real-time to identify trends.",
        backstory="Expert in financial markets using AI for predictions.",
        llm=get_llm(model_name)
    )

    trading_strategy_agent = Agent(
        role="Trading Strategy Developer",
        goal="Develop and test trading strategies based on market analysis.",
        backstory="Quantitative expert refining profitable trading approaches.",
        llm=get_llm(model_name)
    )

    execution_agent = Agent(
        role="Trade Advisor",
        goal="Suggest optimal trade execution strategies.",
        backstory="Specialist in execution timing and market conditions.",
        llm=get_llm(model_name)
    )

    risk_management_agent = Agent(
        role="Risk Advisor",
        goal="Evaluate and provide insights on trading risks.",
        backstory="Risk assessment expert ensuring safe trading strategies.",
        llm=get_llm(model_name)
    )
    
    return [data_analyst_agent, trading_strategy_agent, execution_agent, risk_management_agent]

# Define CrewAI Tasks
def create_tasks(agents, symbol):
    market_analysis_task = Task(
        description=f"Analyze market data and predict trends for {symbol}.",
        agent=agents[0],
        expected_output="A detailed market trend analysis."
    )

    strategy_task = Task(
        description="Develop trading strategies based on market analysis and risk tolerance.",
        agent=agents[1],
        expected_output="A profitable trading strategy tailored to risk tolerance."
    )

    execution_task = Task(
        description="Suggest optimal execution strategies for trades.",
        agent=agents[2],
        expected_output="An execution plan with best timing and market conditions."
    )

    risk_task = Task(
        description="Assess trading risks and suggest mitigation strategies.",
        agent=agents[3],
        expected_output="A risk assessment report with mitigation strategies."
    )
    
    return [market_analysis_task, strategy_task, execution_task, risk_task]

# Function to Run Trading Session
def run_trading_session(symbol, model_name="claude-3-opus"):
    print("\n🚀 Starting Trading Session...")
    print(f"📊 Analyzing {symbol} using {model_name}")
    
    # Create agents and tasks
    agents = create_agents(model_name)
    tasks = create_tasks(agents, symbol)
    
    # Create Crew
    crew = Crew(
        agents=agents,
        tasks=tasks
    )
    
    # Run the crew
    results = crew.kickoff()
    
    # Format and print results
    output = {
        'market_analysis': results[0],
        'trading_strategy': results[1],
        'execution_plan': results[2],
        'risk_assessment': results[3]
    }
    
    print("\n🔍 Market Analysis:")
    print(output['market_analysis'])
    
    print("\n📊 Trading Strategy:")
    print(output['trading_strategy'])
    
    print("\n📈 Trade Execution Plan:")
    print(output['execution_plan'])
    
    print("\n⚠️ Risk Assessment:")
    print(output['risk_assessment'])
    
    return output

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/models')
def get_models():
    return jsonify(list(MODELS.keys()))

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        symbol = data.get('symbol')
        model_name = data.get('model', 'claude-3-opus')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        # Run trading session and get results
        results = run_trading_session(symbol.upper(), model_name)
        return jsonify(results)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)