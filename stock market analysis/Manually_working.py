import google.generativeai as genai
from crewai import Crew, Agent

genai.configure(api_key="AIzaSyCPOGLnUv1-hTp8Qt1GFTI_dJjAPKphbqs")

data_analyst_agent = Agent(
    role="Data Analyst",
    goal="Monitor and analyze market data in real-time to identify trends.",
    backstory="Expert in financial markets using AI for predictions.",
)

trading_strategy_agent = Agent(
    role="Trading Strategy Developer",
    goal="Develop and test trading strategies based on market analysis.",
    backstory="Quantitative expert refining profitable trading approaches.",
)

execution_agent = Agent(
    role="Trade Advisor",
    goal="Suggest optimal trade execution strategies.",
    backstory="Specialist in execution timing and market conditions.",
)

risk_management_agent = Agent(
    role="Risk Advisor",
    goal="Evaluate and provide insights on trading risks.",
    backstory="Risk assessment expert ensuring safe trading strategies.",
)

crew = Crew(agents=[data_analyst_agent, trading_strategy_agent, execution_agent, risk_management_agent])

def analyze_market_data(stock):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Analyze market data and predict trends for {stock}."
    response = model.generate_content(prompt)
    return response.text

def develop_trading_strategy(stock, risk_tolerance, strategy_preference):
    model = genai.GenerativeModel("gemini-pro")
    prompt = (
        f"Develop trading strategies for {stock} with {risk_tolerance} risk tolerance. "
        f"Consider strategy preference: {strategy_preference}."
    )
    response = model.generate_content(prompt)
    return response.text

def plan_trade_execution(stock):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Provide execution strategies for {stock}."
    response = model.generate_content(prompt)
    return response.text

def assess_trade_risk(stock):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Analyze risk factors for trading {stock} and suggest risk mitigation strategies."
    response = model.generate_content(prompt)
    return response.text

def run_trading_session(stock, risk_tolerance, strategy_preference):
    print("🔍 Performing Market Analysis...")
    analysis_result = analyze_market_data(stock)
    print(analysis_result)

    print("\n📊 Developing Trading Strategies...")
    strategy_result = develop_trading_strategy(stock, risk_tolerance, strategy_preference)
    print(strategy_result)

    print("\n📈 Planning Trade Execution...")
    execution_result = plan_trade_execution(stock)
    print(execution_result)

    print("\n⚠️ Assessing Trade Risk...")
    risk_result = assess_trade_risk(stock)
    print(risk_result)

# Example Usage
run_trading_session(
    stock="AAPL",
    risk_tolerance="Medium",
    strategy_preference="Day Trading",
)
