import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return None
