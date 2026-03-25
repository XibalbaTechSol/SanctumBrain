import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Testing key: {api_key}")

try:
    m = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    response = m.invoke("Hello")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")
