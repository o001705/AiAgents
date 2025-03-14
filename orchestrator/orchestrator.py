from phidata.agent import Agent
from agents.financial_advice_agent import FinancialAdviceAgent
from agents.weather_agent import WeatherAgent
from agents.movie_recommendation_agent import MovieRecommendationAgent
from agents.math_agent import MathAgent
from agents.quantum_computing_agent import QuantumComputingAgent
from agents.dlt_agent import DLTAgent
from agents.kyc_agent import KYCVerificationAgent
from agents.credit_decisioning_agent import CreditDecisioningAgent
from agents.document_generation_agent import DocumentGenerationAgent
from agents.retrieval_agent import RetrievalAgent
from embeddings import get_embedding
from db import get_retrieved_documents
import concurrent.futures
import openai

class Orchestrator(Agent):
    def __init__(self):
        super().__init__()
        self.agents = {
            "finance": FinancialAdviceAgent(),
            "weather": WeatherAgent(),
            "movie": MovieRecommendationAgent(),
            "math": MathAgent(),
            "quantum": QuantumComputingAgent(),
            "DLT": DLTAgent(),
            "KYC": KYCVerificationAgent(),
            "credit": CreditDecisioningAgent(),
            "document": DocumentGenerationAgent()
        }

    def process_query(self, question: str, mode="parallel"):
        embedding = get_embedding(question)
        retrieved_documents = get_retrieved_documents(embedding)
        selected_agents = self.select_agents_by_intent(question)
        
        if mode == "parallel":
            return self.process_parallel(selected_agents, question, retrieved_documents)
        else:
            return self.process_serial(selected_agents, question, retrieved_documents)

    def select_agents_by_intent(self, question):
        intent = self.detect_intent(question)
        selected_agents = [agent for key, agent in self.agents.items() if key == intent]
        return selected_agents if selected_agents else [RetrievalAgent()]

    def detect_intent(self, question):
        # Using a simple LLM-based classification
        prompt = f"Identify the category of the following query: {question}\nCategories: finance, weather, movie, math, quantum, DLT, KYC, credit, document."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Classify user questions into predefined categories."},
                      {"role": "user", "content": prompt}]
        )
        intent = response["choices"][0]["message"]["content"].strip().lower()
        return intent if intent in self.agents else "retrieval"

    def synthesize_response(self, responses):
        combined_response = "\n".join([f"{key}: {value}" for key, value in responses.items()])
        synthesis_prompt = f"Synthesize the following information into a concise and clear response:\n{combined_response}"
        synthesis = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Synthesize multiple agent responses into one clear and concise answer."},
                      {"role": "user", "content": synthesis_prompt}]
        )
        return synthesis["choices"][0]["message"]["content"].strip()

    def process_parallel(self, agents, question, context):
        responses = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_agent = {executor.submit(agent.generate_response, question, context): agent for agent in agents}
            for future in concurrent.futures.as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    responses[agent.__class__.__name__] = future.result()
                except Exception as e:
                    responses[agent.__class__.__name__] = str(e)
        return self.synthesize_response(responses)

    def process_serial(self, agents, question, context):
        responses = {}
        for agent in agents:
            try:
                responses[agent.__class__.__name__] = agent.generate_response(question, context)
            except Exception as e:
                responses[agent.__class__.__name__] = str(e)
        return self.synthesize_response(responses)
