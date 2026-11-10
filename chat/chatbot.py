from google import genai
from dotenv import load_dotenv
from rag.retriever import retrieve
import os

load_dotenv()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

# Pull the model name from env, with a real Gemini model as the default.
# The previous hard-coded "gemini-3.6-flash" is not a published model.
_DEFAULT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash")


def ask_retail_ai(question):

    documents = retrieve(question)

    context = "\n\n".join(documents)

    prompt = f"""
You are a helpful AI assistant for a retail store.

Answer the customer's question using ONLY the information
provided in the context below.

If the answer is not available in the context, say:
"I don't have that information."

Do not invent prices, stock levels, policies, offers, or product details.

Context:
{context}

Customer question:
{question}
"""

    response = client.models.generate_content(
        model=_DEFAULT_MODEL,
        contents=prompt
    )

    return response.text