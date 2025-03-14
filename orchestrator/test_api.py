import requests

def test_query():
    question = "What is the weather like today?"
    response = requests.get("http://localhost:8000/query", params={"question": question})
    print(response.json())

if __name__ == "__main__":
    test_query()
