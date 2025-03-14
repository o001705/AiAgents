import requests
import json

url = "http://localhost:9999/chat/"
payload = {
    "user_id": "user_2",
    "message": "What should Mark should do to pull in  his goal by 2 years?"
}

response = requests.post(url, json=payload)
print(response.json()["response"]["content"])
