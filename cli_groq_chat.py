# cli_groq_chat.py
import sys, os, requests, json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

IRRELEVANT_TOPICS = ["news", "stock", "stocks", "cricket", "football", "movie", "politics", "bitcoin", "weather", "sport", "sports"]

def should_refuse(user_message):
    for topic in IRRELEVANT_TOPICS:
        if topic in user_message.lower():
            return True
    return False

def ask_llama(messages, user_message):
    if should_refuse(user_message):
        print("I'm a health assistant and can't answer questions unrelated to health (like news, stocks, sports, etc.). Please ask a health-related question.")
        return
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": 0.15,
        "max_tokens": 400,
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=10)
    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        print(reply)
    else:
        print(f"Groq API error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    json_path = sys.argv[1]
    user_message = sys.argv[2]
    with open(json_path, "r") as f:
        messages = json.load(f)
    ask_llama(messages, user_message)
