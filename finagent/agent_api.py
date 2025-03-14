from fastapi import FastAPI
from fin_agent import phiMultiAgent

app = FastAPI()

@app.post("/chat")
async def chat(request: dict):
    user_input = request.get("message", "")
    agent = phiMultiAgent()
    response = agent.get_response(query=user_input)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)