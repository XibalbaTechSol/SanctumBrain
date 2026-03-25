import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Testing key: {api_key}")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    response = model.generate_content("Hello")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
