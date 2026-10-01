from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

print("1. Starting...")

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

print("2. Client created")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello in one sentence."
)

print("3. Response received")
print(response.text)

print("4. Finished")