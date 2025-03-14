import requests

AGENT_API_URL = "http://localhost:5000/chat"

def chatbot():
    print("CLI Chatbot (Phidata API): Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break

        # Call the phidata agent's API
        response = requests.post(AGENT_API_URL, json={"message": user_input})

        if response.status_code == 200:
            print("Chatbot:", response.json().get("response", "No response from agent"))
        else:
            print("Chatbot: Error communicating with agent.")

if __name__ == "__main__":
    chatbot()
