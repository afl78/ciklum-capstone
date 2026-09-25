import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("🔍 Available Gemini Models for your API key:\n")
for model in client.models.list():
    # Filter for models that support text/content generation
    if "generateContent" in model.supported_actions:
        print(f"• Name: {model.name}")