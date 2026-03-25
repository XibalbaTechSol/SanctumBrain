import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY not found.")
        return

    # Using a dummy model to access the client
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except ImportError:
        print("google-generativeai package not installed. Try pip install google-generativeai")

if __name__ == "__main__":
    list_models()
