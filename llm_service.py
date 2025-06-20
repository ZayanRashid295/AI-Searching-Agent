import requests
from llm_counter import PROGRAMS

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"
def normalize_service_name(name: str) -> str:
    """
    Normalizes service names by removing suffixes like 'application', 'fee', etc.
    """
    suffixes_to_remove = [
        "application", "application fee", "requirements", "documents", "contact",
        "delivery time", "process", "info", "charges", "procedure", "steps"
    ]
    name = name.lower()

    for suffix in suffixes_to_remove:
        if suffix in name:
            name = name.split(suffix)[0]

    # Remove extra symbols and format
    name = name.replace("-", " ").replace("–", " ").strip()
    name = " ".join(word.capitalize() for word in name.split())

    return name

def generate_service_response(name, link, query):
    name = normalize_service_name(name)
    service = PROGRAMS["services"].get(name, {})

    description = service.get("description", "No description available.")
    sector = service.get("sector", "")
    required_documents = service.get("required_documents", {})
    application_fee = service.get("application_fee", {})
    delivery_time = service.get("delivery_time", {})
    coverage = service.get("coverage", "")
    delivery_channels = service.get("delivery_channels", [])
    departments = service.get("departments", [])
    contact = service.get("contact", {})
    meta_tags = service.get("meta_tags", [])
    keywords = service.get("keywords", [])

    prompt = f"""
You are an AI that explains government services.

Service Name: {name}
User Query: {query}

📘 Description:
{description}
"""

    if sector:
        prompt += f"\nSector: {sector}"

    if required_documents:
        prompt += "\n\nRequired Documents:"
        for method, docs in required_documents.items():
            prompt += f"\n- {method}:\n" + "\n".join(f"  • {doc}" for doc in docs)

    if application_fee:
        prompt += "\n\nApplication Fee:"
        if isinstance(application_fee, dict):
            for method, fee in application_fee.items():
                if isinstance(fee, dict):
                    prompt += f"\n- {method}:\n" + "\n".join(f"  • {k}: {v}" for k, v in fee.items())
                else:
                    prompt += f"\n- {method}: {fee}"
        else:
            prompt += f"\n- {application_fee}"

    if delivery_time:
        prompt += "\n\nDelivery Time:"
        if isinstance(delivery_time, dict):
            for method, time in delivery_time.items():
                if isinstance(time, dict):
                    prompt += f"\n- {method}:\n" + "\n".join(f"  • {k}: {v}" for k, v in time.items())
                else:
                    prompt += f"\n- {method}: {time}"
        else:
            prompt += f"\n- {delivery_time}"

    if coverage:
        prompt += f"\n\nCoverage: {coverage}"

    if delivery_channels:
        prompt += "\n\nDelivery Channels:\n" + "\n".join(f"- {ch}" for ch in delivery_channels)

    if departments:
        prompt += "\n\nDepartments:\n" + "\n".join(f"- {d}" for d in departments)

    if contact:
        prompt += "\n\nContact:"
        if "helpline" in contact:
            prompt += "\n- Helpline(s): " + ", ".join(contact["helpline"])
        if "phone" in contact:
            prompt += "\n- Phone(s): " + ", ".join(contact["phone"])

    if meta_tags:
        prompt += "\n\nMeta Tags:\n" + ", ".join(meta_tags)

    if keywords:
        prompt += "\n\nKeywords:\n" + ", ".join(keywords)

    prompt += """
\nInstructions:
- Use ONLY the provided info to answer.
- Be helpful, clear, and concise.
- Don’t invent or add anything.
"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        })
        generated = response.json()["response"].strip()
    except Exception:
        generated = description

    return {
        "title": name,
        "link": link,
        "description": generated
    }
