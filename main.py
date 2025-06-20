from fastapi import FastAPI
from pydantic import BaseModel
from llm_router import classify_query
from llm_initiative import generate_initiative_response
from llm_service import generate_service_response
from llm_counter import PROGRAMS, generate_count_response
import requests

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

    # Resolve vague terms like "it" or "this"
    vague_terms = ["it", "this", "that", "they", "them", "their", "its", "they're"]
    if any(word in query for word in vague_terms) and user_context["last_name"]:
        for term in vague_terms:
            query = query.replace(term, user_context["last_name"].lower())

    # Greet the user
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

    # Classify query
    intent_data = classify_query(query)
    intent = intent_data.get("intent", "unknown").lower()
    name = intent_data.get("name", "")
    link = intent_data.get("link", "")

    # Save for vague future reference
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

    # Program count intent
    if intent in ["count_services", "count_initiatives", "total_programs", "count_programs"]:
        return generate_count_response(intent, query)

    # List all
    elif intent in ["initiatives", "services"] and name == "summary":
        return {
            "intent": intent,
            "name": "summary",
            "title": f"All Government {intent.capitalize()}",
            "link": link,
            "description": f"The government is currently offering {len(PROGRAMS[intent])} {intent}: " +
                           ", ".join(list(PROGRAMS[intent].keys())) + "."
        }

    # Specific initiative or service
    elif intent == "initiative":
        return {
            "intent": intent,
            "name": name,
            **generate_initiative_response(name, link, query)
        }

    elif intent == "service":
        return {
            "intent": intent,
            "name": name,
            **generate_service_response(name, link, query)
        }

    # Chitchat fallback
    elif intent in ["summary", "unknown"] and query:
        fallback_prompt = f"""
You are a friendly AI assistant that helps citizens explore government services in Pakistan.

However, the user asked something unrelated:

User Query: "{query}"

Respond in a warm, helpful, and human tone. If possible, gently guide them to ask about government services like birth certificates or apni zameen initiatives.
Avoid robotic replies. Keep it short and friendly.
"""
        try:
            res = requests.post(OLLAMA_URL, json={
                "model": MODEL,
                "prompt": fallback_prompt,
                "stream": False
            })
            chat_response = res.json()["response"].strip()
        except Exception:
            chat_response = (
                "I'm here to help you with government services like housing, CNICs, or certificates. "
                "Try asking me about those!"
            )

        return {
            "intent": "chitchat",
            "name": "general",
            "title": "Let's Chat",
            "description": chat_response
        }

    # Final fallback
    return {
        "intent": intent,
        "name": name,
        "title": "Unknown",
        "link": "#",
        "description": "Could not classify your query."
    }
