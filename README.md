# Curo: Personalized Health Assistant with Intelligent Prescription Reader

> **Curo** is an AI-powered, feedback-driven health assistant designed to provide safe, up-to-date, and personalized medical guidance.  
> Curo combines large language models (LLMs), real-time web retrieval, an intelligent prescription reader, and a robust user feedback loop to deliver truly user-centric health advice.

---

## Features

- **Personalized Health Guidance:**  
  Tailors answers using user’s health profile (age, gender, conditions, medications, allergies).

- **LLM-Powered Chatbot:**  
  Backed by a health-specialized Llama LLM (simulated fine-tuning), providing context-aware responses.

- **Real-Time Web Retrieval:**  
  Fetches the latest medical articles and drug information via APIs and web scraping.

- **Intelligent Prescription Reader:**  
  Extracts medicine names and dosages from uploaded prescription images, explains them, and provides buy links and trusted sources.

- **Continuous Feedback Loop:**  
  Users rate every chat or prescription summary; feedback is analyzed in real time, powering RLHF-inspired improvement.

- **Analytics Dashboard:**  
  Visualizes model performance and user satisfaction trends.

- **Secure MySQL Database:**  
  All user data, conversations, and feedback are stored securely.

- **User Authentication:**  
  Secure sign-up, login, and health profile management.

---

## Architecture Overview

- **Frontend:** Streamlit-based UI for chat, feedback, prescription uploads, and analytics.
- **LLM Chatbot:** Health-focused Llama LLM, prompted with user profile.
- **Retrieval Module:** Web/API-based retrieval for up-to-date info.
- **Prescription Reader:** OCR (Gemini Vision API) + medicine extraction.
- **Feedback Module:** Captures and stores ratings for continuous learning.
- **Analytics Dashboard:** Visualizes feedback and safety metrics.
- **MySQL Database:** Secure storage for all data.

---

### Prerequisites

- Python 3.9+
- MySQL database (local or remote)
- API keys for Tavily (web search) and Gemini Vision (OCR)
- pip, virtualenv (recommended)

### Setup Instructions

```bash
git clone https://github.com/yourusername/curo-health-assistant.git
cd curo-health-assistant

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

MYSQL_URI=mysql+pymysql://<user>:<password>@<host>/<database>
TAVILY_API_KEY=your-tavily-key
GEMINI_API_KEY=your-gemini-key
SECRET_KEY=your-secret-key

python -c "from db import init_db; init_db()"

streamlit run app.py

streamlit run feedback.py

app.py                # Main Streamlit app
feedback.py           # Feedback analytics dashboard
db.py                 # Database models & connection
cli_groq_chat.py      # LLM chat interface script
cli_gemini_prescription.py  # Prescription OCR/LLM script
requirements.txt
.env.example
README.md
