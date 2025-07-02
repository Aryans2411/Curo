# cli_gemini_prescription.py
import sys, os, requests, base64
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def downscale_image(file_path, max_dim=800):
    image = Image.open(file_path)
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.thumbnail((max_dim, max_dim))
    buf = io.BytesIO()
    image.save(buf, format='JPEG')
    return buf.getvalue()

def extract_prescription_info(file_bytes, filename):
    encoded_string = base64.b64encode(file_bytes).decode()
    mime_type = "image/png" if filename.lower().endswith("png") else "image/jpeg"
    headers = { "Content-Type": "application/json" }
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Extract all medication names, dosages, frequencies, and doctor comments from this prescription. "
                            "Give a short summary for the patient in plain English. Also, mention what each medicine is generally used for if possible. "
                            "Format medicine names clearly as a markdown list for extraction."
                        )
                    },
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": encoded_string
                        }
                    }
                ]
            }
        ]
    }
    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=45)
    if response.status_code == 200:
        try:
            print(response.json()['candidates'][0]['content']['parts'][0]['text'])
        except Exception as e:
            print("Error parsing Gemini response:", e)
            print(response.text)
    else:
        print(f"Gemini API error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    file_path = sys.argv[1]
    file_bytes = downscale_image(file_path)
    extract_prescription_info(file_bytes, file_path)
