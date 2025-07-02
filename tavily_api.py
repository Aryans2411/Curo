import os, requests
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_API_URL = "https://api.tavily.com/search"

def get_health_articles(query):
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "num_results": 5,
        "search_depth": "basic",
        "include_answer": False,
        "include_images": False
    }
    response = requests.post(TAVILY_API_URL, headers=headers, json=payload, timeout=10)
    if response.status_code == 200:
        res = response.json()
        return [{
            "title": item["title"], "url": item["url"]
        } for item in res.get("results", [])[:5]]
    else:
        return []

def get_medicine_links(medicine_names):
    results = []
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }
    for name in medicine_names:
        payload = {
            "query": f"medical uses, dosage, and side effects of {name}",
            "num_results": 1,
            "search_depth": "basic",
            "include_answer": False,
            "include_images": False
        }
        try:
            response = requests.post(TAVILY_API_URL, headers=headers, json=payload, timeout=6)
            if response.status_code == 200:
                res = response.json()
                results.extend([{
                    "medicine": name,
                    "title": item["title"],
                    "url": item["url"]
                } for item in res.get("results", [])[:1]])
        except Exception:
            pass
    return results
