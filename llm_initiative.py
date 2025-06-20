import requests
from llm_counter import PROGRAMS

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


def generate_initiative_response(name, link, query):
    name = name.split(" - ")[0].strip()

    program = PROGRAMS["initiatives"].get(name, {})
    description = program.get("description", "No description available.")
    eligibility = program.get("eligibility", [])
    application_process = program.get("application_process", [])
    contact = program.get("contact", {})
    scope = program.get("scope", [])
    phases = program.get("phases", {})

    prompt = f"""
You are an AI that explains government initiatives.

Initiative Name: {name}
User Query: {query}

Description:
{description}
"""

    if eligibility:
        prompt += "\nEligibility:\n" + "\n".join(f"- {item}" for item in eligibility)

    if application_process:
        prompt += "\n\nApplication Process:\n" + "\n".join(f"Step {i+1}: {step}" for i, step in enumerate(application_process))

    if contact:
        prompt += "\n\nContact:\n"
        if "helpline" in contact:
            prompt += f"- Helpline: {contact['helpline']}\n"
        if "phone" in contact:
            prompt += f"- Phone: {', '.join(contact['phone'])}\n"

    if scope:
        prompt += "\nDistricts Covered:\n" + ", ".join(scope)

    if phases:
        prompt += "\n\nPhases:\n"
        for phase, info in phases.items():
            prompt += f"- {phase.title()}: {info['plots']} plots in {info['schemes']} schemes across {info['districts']} districts.\n"

    prompt += """
\nInstructions:
- Use ONLY the provided information to answer the user's query.
- Do NOT invent or add any information.
- Paraphrase or summarize clearly in 1–3 lines.
- Be professional and helpful.
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
