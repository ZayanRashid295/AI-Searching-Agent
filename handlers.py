import json

def initiative_handler(query: str):
    try:
        with open("data/initiatives.json", "r", encoding="utf-8") as f:
            initiatives = json.load(f)

        query = query.lower()

        for item in initiatives:
            keywords = item.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in query:
                    return item

    except Exception as e:
        print("Error in initiative_handler:", e)

    return {
        "title": "Unknown Initiative",
        "link": "#",
        "description": "No match found"
    }

def service_handler(query: str):
    try:
        with open("data/service.json", "r", encoding="utf-8") as f:
            services = json.load(f)
            print("services: ", services, type(services))
            return services
       

    except Exception as e:
        print("Error in service_handler:", e)

    return {
        "title": "Unknown Service",
        "link": "#",
        "description": "No match found"
    }
