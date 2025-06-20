import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

def get_intent_from_llm(prompt: str) -> str:
    full_prompt = (
        "You are a classifier AI. Below are the current government services and initiatives:\n\n"
        "Services:\n"
        "- Title: Birth Certificate or Domicile Registration \n"
        "  Description: Key service for birth and domicile registration, ensuring every child has a legal identity.\n"
        " return  should = "
        "Initiatives:\n"
        "- Title: Apni Zameen Apna Ghar\n"
        "  Description: initiative right now by government is Apni Zameen Apna Ghar.\n\n"
        "keywords: initiative, government, Apni Zameen Apna Ghar, گھر,shelter\n\n"
        "When a user provides a query, classify it as either:\n"
        "- \"service\": if the query is about who can apply, criteria, qualifications, requirements, or anything related to the process or eligibility for a service (e.g., birth certificate).\n"
        "- \"initiative\": if the query is about the existence, name, launch, or general information about a government initiative (e.g., Apni Zameen Apna Ghar).\n\n"
        "Respond with only one word: either \"service\" or \"initiative\".\n\n"
        f"User Query: {prompt}\nIntent:"
)


    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False
        })

        print("Ollama Raw Response:", response.text)
        text = response.json().get("response", "").lower()
        print("Ollama Processed Response:", text)
        if "initiative" in text:
            return "initiative"
        elif "service" in text:
            return "service"
    except Exception as e:
        print("Error in intent classification:", e)

    return "unknown"
