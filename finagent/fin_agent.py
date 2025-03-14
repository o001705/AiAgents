from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from NseTool import NseIndiaTool
from phi.tools.duckduckgo import DuckDuckGo

import os
import io
from dotenv import load_dotenv

class phiMultiAgent:
    def create_agent(self):

        self.model_name = "deepseek-r1-distill-qwen-32b"

        # Web Serch Agent
        web_search_agent = Agent(
            name='web_search_agent',
            model=Groq(id=self.model_name),
            tools=[DuckDuckGo()],
            role="Search the web for inormation on a given topic",
            instructions=["Always include sources", "Use the most reliable sources"],
            show_tools_calls=True,
            markdown=True,

        )

        #Financial Agent
        fin_agent = Agent(
            name='fin_agent',
            model=Groq(id=self.model_name),
            tools=[
                YFinanceTools(stock_price=True, 
                            stock_fundamentals=True, 
                            analyst_recommendations=True,
                            company_news=True),
                NseIndiaTool(stock_quote=True, stock_info=True)
                ],
            role="Get financial information on a given stock",
            instructions=["Use Tables to display Data"],
            show_tools_calls=True,
            markdown=True,
        )

        # Add the agents to the list of agents

        agents = [web_search_agent, fin_agent]

        #create a multi_agent with this list of agents
        multi_agent = Agent(
            team=agents, 
            name='multi_agent', 
            model=Groq(id=self.model_name),
            role="A multi-agent that can perform multiple tasks", 
            instructions=["Use Tables to display Data", "Always include sources", "Use the most reliable sources"],
            markdown=True,
        )

        return multi_agent

    def __init__(self):
        self.history = []  # Store queries if needed    
        load_dotenv("agent.env")
        self.multi_agent = self.create_agent()


    def get_response(self, query):
        print("QUERY:", query)
        self.history.append(query)
        response = self.multi_agent.run(query,  markdown=True)

        # Extract the response content correctly
        if hasattr(response, "content"):
            response_text = response.content.strip()
        else:
            response_text = str(response).strip()  # Convert to string as fallback        formatted_response = f"{response.strip()}\n"

        # Formatting response for better readability
        formatted_response = f"\n🗣️ **Chatbot Response:**\n{response_text}\n"

        return formatted_response
    #multi_agent.print_response("Summerize the specialist recommendations and share the latest news for AAPL?")