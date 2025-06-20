import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

def classify_query(query):
    prompt = f"""
You are a JSON-only AI classifier and extractor.

The government currently offers:

Initiatives:
1. Apni Zameen Apna Ghar – Housing/Shelter


Services:
1. Birth Certificate – Legal identity

Instructions:
1. Classify the user query using one of these intents:
   - "initiative"           → for a specific initiative (e.g. Digital Pakistan)
   - "service"              → for a specific service (e.g. CNIC Application)
   - "count_services"       → if it's about how many services or describing them
   - "count_initiatives"    → if it's about how many initiatives or describing them
   - "total_programs"       → if it's asking for total government programs (both)
   - "summary"              → if user says something vague like "hi", "hello", "info", "help"

2. If user is asking for a specific program, set:
   - "name" to the program title (e.g. "Digital Pakistan")
   - "link" to a mock government URL like "https://gov.pk/digital-pakistan"

3. If general question (e.g., "how many initiatives"), set:
   - name = "summary"
   - link = general section link, like "https://gov.pk/initiatives" or "https://gov.pk/services"

4. Always respond in this **exact JSON format**:
{{"intent": "...", "name": "...", "link": "..."}}

User Query: {query}
"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })

    try:
        return eval(response.json()["response"])
    except Exception as e:
        print("Router LLM error:", e)
        return {"intent": "unknown", "name": ""}
