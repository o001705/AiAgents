from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import numpy as np
from phi.agent import Agent
from phi.model.groq import Groq
from DBConnection import DBAction
import uvicorn

# Initialize FastAPI app
load_dotenv("agent.env")
app = FastAPI()

model_name = "deepseek-r1-distill-qwen-32b"
db_action = DBAction()

#Financial Agent
fin_agent = Agent(
    name='fin_agent',
    model=Groq(id= model_name),
    tools=[],
    role="Give financial advise based on user profile",
    instructions=["Use the most reliable sources", "Always include sources"],
    show_tools_calls=True,
    markdown=True,
)

# Initialize Groq client
#GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#groq_client = GroqClient(api_key=GROQ_API_KEY)

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat/")
def chat(request: ChatRequest):
    user_id = request.user_id
    message = request.message
    
    user_data = db_action.get_user_profile(user_id)

    if user_data == {}:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate and store a random transaction
    db_action.store_new_transaction(user_id)

    #get chat history of the user
    past_chat = db_action.retrieve_chat_memory(user_id)
    
    # AI response with personalization
    prompt = f"User Profile: {user_data}\nPast Chat: {past_chat}\nUser: {message}\nAgent:" 
    
    # Use PHIData Agent for inference
    ai_response = fin_agent.run(prompt)

    # Store new interaction in database
    embedding = np.random.rand(1538).tolist()  # Replace with real embedding model
    db_action.store_chat_memory(user_id, embedding, message)
        
    return {"response": ai_response}

if __name__ == "__main__":  # This makes it executable via `python Personalization.py`
    uvicorn.run("Personalization:app", host="0.0.0.0", port=9999, reload=True)