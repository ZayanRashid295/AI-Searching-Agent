import requests

URL = "http://127.0.0.1:8000/search"

test_queries = [
    "hi",
    "Tell me about apni zameen",
    "How do I get a birth certificate?",
    "List all services",
    "How many initiatives are there?",
    "What is the process for CNIC renewal?",
    "this service",
    "Can you help me?",
    "asalamualaikum"
]

for q in test_queries:
    resp = requests.post(URL, json={"query": q})
    print(f"Query: {q}")
    print("Response:", resp.json())
    print("-" * 40)
