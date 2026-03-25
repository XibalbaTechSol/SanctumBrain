import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(f"Testing key: {api_key}")

try:
    # Try different model name
    m = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
    response = m.invoke("Hello")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")
