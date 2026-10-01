import time
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


def create_embedding(text, max_retries=3):

    for attempt in range(max_retries):

        try:

            response = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text
            )

            return response.embeddings[0].values

        except Exception as error:

            print(
                f"Embedding failed "
                f"(attempt {attempt + 1}/{max_retries})"
            )

            print(error)

            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** attempt

            print(
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)