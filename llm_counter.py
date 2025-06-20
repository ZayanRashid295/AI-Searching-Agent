import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

PROGRAMS = {
    "initiatives": {
        "Apni Zameen Apna Ghar": {
            "description": "The Apni Zameen Apna Ghar Program is a Punjab government initiative aimed at providing free 3-marla residential plots to poor and homeless individuals across 19 districts. It operates through PHATA with transparent balloting, strict eligibility, and an online portal for application.",
            "link": "https://azag.punjab.gov.pk/",
            "eligibility": [
                "Permanent resident of Punjab (valid CNIC).",
                "Application must be for own district.",
                "No owned plot/house by applicant, spouse, or dependents anywhere in Pakistan.",
                "No criminal record or financial default.",
                "Accurate information is mandatory; false declarations lead to disqualification."
            ],
            "application_process": [
                "Register/login to the portal.",
                "Fill application form with personal, income, and document details.",
                "Upload documents.",
                "Submit form and track status online."
            ],
            "contact": {
                "helpline": "0800-09100",
                "phone": ["042-99213419", "042-99213428"]
            },
            "scope": [
                "Attock", "Bahawalnagar", "Bahawalpur", "Bhakkar", "Chiniot", "Faisalabad", "Gujrat",
                "Jhang", "Jhelum", "Kasur", "Khushab", "Layyah", "Lodhran", "Mandi Baha-Ud-Din", "Okara",
                "Rajanpur", "Sahiwal", "Sargodha", "Vehari"
            ],
            "phases": {
                "phase_1": {
                    "plots": 1892,
                    "schemes": 23,
                    "districts": 19
                }
            }
        }
    },
    "services": {
        "Birth Certificate": {
                "sector": "Local Government Services",
                "link": "https://gov.pk/birth-certificate",
                "description": "A birth certificate is an official document that confirms an individual's birth details—such as name, date, place, and parentage—based on NADRA's verified records. It is used for legal, educational, and official purposes.",
                "required_documents": {
                    "Union Council": [
                        "Copies of the parents’ CNICs",
                        "Birth certificate from hospital/traditional birth attendant",
                        "Completed Union Council application form with signature/thumb impression"
                    ],
                    "e-Khidmat Markaz": [
                        "Application Form A",
                        "Applicant’s CNIC",
                        "Birth slip (if born in hospital)",
                        "Vaccination card",
                        "Parents’ CNICs",
                        "Paternal grandfather’s CNIC"
                    ],
                    "Dastak Application": [
                        "Application Form A",
                        "Two recent child photos",
                        "Applicant’s CNIC",
                        "Parents’ CNICs",
                        "If home birth: CNICs of two witnesses",
                        "Vaccination card",
                        "Hospital-issued certificate",
                        "Paternal grandfather’s CNIC/death certificate (optional)",
                        "Rs. 300 affidavit"
                    ]
                },
                "application_fee": {
                    "Union Council": "Free for registration, Rs. 100 for NADRA computerized certificate",
                    "e-Khidmat Markaz": {
                        "Within 60 days": "Rs. 200",
                        "61 days to 2 years": "Rs. 200"
                    },
                    "Dastak Application": "Rs. 969"
                },
                "delivery_time": {
                    "Union Council": {
                        "Standard": "3 working days",
                        "Delayed (61 days–7 years)": "7 working days",
                        "Delayed (7+ years)": "20 working days"
                    },
                    "e-Khidmat Markaz": "7 working days",
                    "Dastak Application": "9 working days"
                },
                "coverage": "All districts of Punjab",
                "delivery_channels": [
                    "Union Council (Department Visit)",
                    "e-Khidmat Centers (Department Visit)",
                    "Dastak App (Doorstep Delivery)"
                ],
                "departments": [
                    "NADRA",
                    "Local Government & Community Development",
                    "District Government",
                    "Union Council Office"
                ],
                "contact": {
                    "helpline": [
                        "1202 (Dastak Doorstep Delivery)",
                        "0800-09100 (e-Khidmat Center)"
                    ],
                    "phone": [
                        "+92-42-99232123 (e-Khidmat Center)"
                    ]
                },
                "meta_tags": [
                    "Birth certificate from e-Khidmat Center",
                    "Birth registration through Maryam Ki Dastak"
                ],
                "keywords": [
                    "Birth certificate",
                    "birth registration",
                    "online birth certificate service",
                    "birth certificate through e-Khidmat Center",
                    "Dastak delivery for birth certificate",
                    "birth certificate Maryam ki Dastak",
                    "issuance of birth certificate",
                    "birth certificate fee",
                    "required documents for birth certificate"
                ]
}
 }
}


def generate_count_response(intent, query):
    count_initiatives = len(PROGRAMS["initiatives"])
    count_services = len(PROGRAMS["services"])
    total = count_initiatives + count_services

    query_lower = query.lower()
    show_programs = any(word in query_lower for word in [
        "list", "show", "which", "name", "detail", "what are", "elaborate", "describe"
    ])

    # Build program descriptions for LLM (used in prompt only)
    initiatives_description = "\n".join(
        [f"- {name}: {data['description']}" for name, data in PROGRAMS["initiatives"].items()])
    services_description = "\n".join(
        [f"- {name}: {data['description']}" for name, data in PROGRAMS["services"].items()])

    prompt = f"""
You are an AI assistant that explains government programs.

Available:
- Initiatives: {count_initiatives}
- Services: {count_services}
- Total Programs: {total}

Initiative Descriptions:
{initiatives_description}

Service Descriptions:
{services_description}

User Query: "{query}"

Instructions:
- If the query is about the number of services, respond: "There are {count_services} services."
- If it's about the number of initiatives, say: "There are {count_initiatives} initiatives."
- If the user asks about all programs or total, reply: "There are {total} programs in total."
- If the user asks for details (e.g., 'list', 'describe', 'elaborate'), provide a short human-friendly summary using the descriptions above.
- If the user mentions a specific program, summarize only that one with its description and link.
- Only use the provided descriptions. Do not make up or add extra info.
- If the query is unclear, return a general summary of program counts only.
"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        })
        description = response.json()["response"].strip()
    except Exception:
        # Basic fallback response
        if intent == "count_services":
            description = f"There are {count_services} services."
        elif intent == "count_initiatives":
            description = f"There are {count_initiatives} initiatives."
        else:
            description = f"The government currently offers {count_initiatives} initiatives and {count_services} services."

    result = {
        "intent": intent,
        "name": "summary",
        "title": "Program Count",
        "description": description
    }

    if show_programs:
        detailed_programs = []

        if intent == "count_services":
            selected_categories = ["services"]
        elif intent == "count_initiatives":
            selected_categories = ["initiatives"]
        elif intent == "total_programs":
            selected_categories = ["services", "initiatives"]
        else:
            selected_categories = []

        for category in selected_categories:
            for name, data in PROGRAMS[category].items():
                detailed_programs.append({
                    "name": name,
                    "link": data["link"],
                    
                })

        result["programs"] = detailed_programs

    return result
