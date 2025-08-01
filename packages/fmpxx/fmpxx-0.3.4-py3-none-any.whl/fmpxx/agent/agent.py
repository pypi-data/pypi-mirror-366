import os
import json
from typing import Optional
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import Toolkit

from .tools import FinancialsTools, StocksTools


class FinAIAgent:
    """
    Financial AI Agent powered by phidata framework.
    
    This agent can understand natural language queries about:
    - Stock market data (prices, quotes, historical data)
    - Company financials (income statements, balance sheets, cash flow)
    """
    
    def __init__(self, api_key: Optional[str] = None, gemini_api_key: Optional[str] = None):
        """
        Initialize the Financial AI Agent.
        
        Args:
            api_key: FMP API key (if not provided, will try to read from environment)
            gemini_api_key: Google Gemini API key (if not provided, will try to read from environment)
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv("FMP_KEY")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("FMP API key is required. Set FMP_KEY environment variable or pass api_key parameter.")
        
        if not self.gemini_api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass gemini_api_key parameter.")
        
        # Initialize tools
        self.financials_tools = FinancialsTools(self.api_key)
        self.stocks_tools = StocksTools(self.api_key)
        
        # Create the agent
        self.agent = Agent(
            name="Financial AI Agent",
            model=Gemini(id="gemini-2.5-flash"),
            tools=[self.financials_tools, self.stocks_tools],
            description="A financial analysis agent that can retrieve stock data and company financials",
            instructions=[
                "You are a helpful financial analysis assistant.",
                "You can access stock market data and company financial statements.",
                "Always provide clear, concise answers with relevant data.",
                "When providing financial data, format it in an easy-to-understand way.",
                "If you can't find data for a specific symbol, let the user know.",
                "Be specific about the time periods and data you're providing.",
                "You can respond in both English and Chinese based on the user's language."
            ],
            markdown=True,
            show_tool_calls=True,
            add_datetime_to_instructions=True,
        )
    
    def query(self, question: str) -> str:
        """
        Query the financial AI agent with a natural language question.
        
        Args:
            question: Natural language question about stocks or financial data
            
        Returns:
            Agent's response with relevant data
        """
        try:
            response = self.agent.run(question)
            return response.content
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def chat(self):
        """
        Start an interactive chat session with the financial AI agent.
        """
        print("🤖 Financial AI Agent")
        print("I can help you with stock data and company financials.")
        print("Type 'exit' or 'quit' to end the conversation.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Agent: Goodbye! 👋")
                    break
                
                if not user_input:
                    continue
                
                print("Agent: ", end="")
                response = self.query(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\nAgent: Goodbye! 👋")
                break
            except Exception as e:
                print(f"Agent: Error - {str(e)}\n")


def create_agent(api_key: Optional[str] = None, gemini_api_key: Optional[str] = None) -> FinAIAgent:
    """
    Factory function to create a Financial AI Agent.
    
    Args:
        api_key: FMP API key
        gemini_api_key: Google Gemini API key
        
    Returns:
        FinAIAgent instance
    """
    return FinAIAgent(api_key=api_key, gemini_api_key=gemini_api_key)