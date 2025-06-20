from fastapi import FastAPI
from pydantic import BaseModel
from llm_router import classify_query
from llm_initiative import generate_initiative_response
from llm_service import generate_service_response
import requests
from llm_counter import PROGRAMS  # import programs

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

# Simple memory for one session
user_context = {
    "last_intent": None,
    "last_name": None,
    "last_link": None,
    "last_query": None
}

@app.post("/search")
async def search_handler(payload: QueryRequest):
    query = payload.query.strip().lower()
    session_id = "default"

    vague_terms = ["it", "this", "that", "they", "them", "their", "its", "they're"]
    if any(word in query for word in vague_terms) and user_context["last_name"]:
        # Replace vague terms with last referred name
        for term in vague_terms:
            query = query.replace(term, user_context["last_name"].lower())

    
    if query in ["hi", "hello", "hey", "salam", "asalamualaikum"]:
        count_initiatives = len(PROGRAMS["initiatives"])
        count_services = len(PROGRAMS["services"])
        total = count_initiatives + count_services

        example_initiative = list(PROGRAMS["initiatives"].keys())[0]
        example_service = list(PROGRAMS["services"].keys())[0]

        greeting_prompt = f"""
You are a helpful and friendly AI assistant that welcomes users.

Program Stats:
- Total: {total}
- Initiatives: {count_initiatives}
- Services: {count_services}
- Example Initiative: {example_initiative}
- Example Service: {example_service}

User says: '{query}'

Generate a short 2–3 line welcome message that:
1. Greets the user warmly.
2. Mentions you can help with government programs and services.
3. Suggests asking about options like '{example_initiative}' or '{example_service}'.
Use plain English. Be clear and friendly.
"""

        try:
            res = requests.post(OLLAMA_URL, json={
                "model": MODEL,
                "prompt": greeting_prompt,
                "stream": False
            })
            message = res.json()["response"].strip()
        except Exception:
            message = (
                f"Hello! I'm your assistant for exploring {count_initiatives} initiatives "
                f"and {count_services} services.\n"
                f"Try asking about '{example_initiative}' or how to get a '{example_service}'."
            )

        return {
            "intent": "greeting",
            "name": "general",
            "title": "Welcome!",
            "description": message
        }

    # Classification
    intent_data = classify_query(query)
    intent = intent_data.get("intent", "unknown").lower()
    name = intent_data.get("name", "")
    link = intent_data.get("link", "")

        # Save to context for future vague references
    if name and name != "summary":
        user_context["last_name"] = name
        user_context["last_intent"] = intent
        user_context["last_link"] = link
        user_context["last_query"] = query
    elif intent == "count_initiatives":
        user_context["last_intent"] = "initiative"
        user_context["last_query"] = query
        user_context["last_name"] = list(PROGRAMS["initiatives"].keys())[0]
        user_context["last_link"] = PROGRAMS["initiatives"][user_context["last_name"]]["link"]
    elif intent == "count_services":
        user_context["last_intent"] = "service"
        user_context["last_query"] = query
        user_context["last_name"] = list(PROGRAMS["services"].keys())[0]
        user_context["last_link"] = PROGRAMS["services"][user_context["last_name"]]["link"]


    # Program count response
    if intent in ["count_services", "count_initiatives", "total_programs", "count_programs"]:
        from llm_counter import generate_count_response
        return generate_count_response(intent, query)

    #  Full listing
    elif intent in ["initiatives", "services"] and name == "summary":
        return {
            "intent": intent,
            "name": "summary",
            "title": f"All Government {intent.capitalize()}",
            "link": link,
            "description": f"The government is currently offering {len(PROGRAMS[intent])} {intent}: " +
                           ", ".join(list(PROGRAMS[intent].keys())) + "."
        }

    #  Individual response
    elif intent == "initiative":
        result = generate_initiative_response(name, link, query)

    elif intent == "service":
        result = generate_service_response(name, link, query)

    #  General summary
    elif intent == "summary":
        result = {
            "title": "Government Programs Summary",
            "link": link,
            "description": "The government is currently offering various services and initiatives. Please specify your query for more details."
        }

    #  Unknown
    else:
        result = {
            "title": "Unknown",
            "link": "#",
            "description": "Could not classify your query."
        }

    return {
        "intent": intent,
        "name": name,
        **result
    }
