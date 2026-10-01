from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

print("1. Starting...")

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

print("2. Client created")

text = "India Gate Basmati Rice is available in aisle A-15."

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=text
)

print("3. Embedding created")

embedding = response.embeddings[0].values

print("Number of dimensions:", len(embedding))
print("First 10 values:", embedding[:10])

print("4. Finished")