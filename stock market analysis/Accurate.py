import google.generativeai as genai
from crewai import Crew, Agent, Task

genai.configure(api_key="INSERT API KEY HERE")

def generate_response(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

data_analyst_agent = Agent(
    role="Data Analyst",
    goal="Monitor and analyze market data in real-time to identify trends.",
    backstory="Expert in financial markets using AI for predictions."
)

trading_strategy_agent = Agent(
    role="Trading Strategy Developer",
    goal="Develop and test trading strategies based on market analysis.",
    backstory="Quantitative expert refining profitable trading approaches."
)

execution_agent = Agent(
    role="Trade Advisor",
    goal="Suggest optimal trade execution strategies.",
    backstory="Specialist in execution timing and market conditions."
)

risk_management_agent = Agent(
    role="Risk Advisor",
    goal="Evaluate and provide insights on trading risks.",
    backstory="Risk assessment expert ensuring safe trading strategies."
)

# Define CrewAI Tasks
market_analysis_task = Task(
    description="Analyze market data and predict trends for a stock.",
    agent=data_analyst_agent,
    expected_output="A detailed market trend analysis."
)

strategy_task = Task(
    description="Develop trading strategies based on market analysis and risk tolerance.",
    agent=trading_strategy_agent,
    expected_output="A profitable trading strategy tailored to risk tolerance."
)

execution_task = Task(
    description="Suggest optimal execution strategies for trades.",
    agent=execution_agent,
    expected_output="An execution plan with best timing and market conditions."
)

risk_task = Task(
    description="Assess trading risks and suggest mitigation strategies.",
    agent=risk_management_agent,
    expected_output="A risk assessment report with mitigation strategies."
)

# Create Crew with Tasks
crew = Crew(agents=[data_analyst_agent, trading_strategy_agent, execution_agent, risk_management_agent],
            tasks=[market_analysis_task, strategy_task, execution_task, risk_task])

# Function to Run Trading Session
def run_trading_session():
    print("\n🚀 Starting Trading Session...")
    results = crew.kickoff()
    
    print("\n🔍 Market Analysis:")
    print(results[0])
    
    print("\n📊 Trading Strategy:")
    print(results[1])
    
    print("\n📈 Trade Execution Plan:")
    print(results[2])
    
    print("\n⚠️ Risk Assessment:")
    print(results[3])

# Example Usage
run_trading_session()
