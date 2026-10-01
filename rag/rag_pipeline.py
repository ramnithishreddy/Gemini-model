from ingestion.embedder import create_embedding
from rag.similarity import cosine_similarity
from rag.vector_store import load_vectors

from google import genai
from dotenv import load_dotenv

import os


load_dotenv()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


def retrieve(question, top_k=2):

    chunks = load_vectors()

    question_embedding = create_embedding(question)

    results = []

    for chunk in chunks:

        score = cosine_similarity(
            question_embedding,
            chunk["embedding"]
        )

        results.append({
            "source": chunk["source"],
            "text": chunk["text"],
            "score": score
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]


def ask(question):

    # -------------------------
    # Retrieve
    # -------------------------

    results = retrieve(
        question,
        top_k=2
    )

    # -------------------------
    # Build context
    # -------------------------

    context = "\n\n".join(
        f"Source: {result['source']}\n"
        f"{result['text']}"
        for result in results
    )

    # -------------------------
    # Prompt Gemini
    # -------------------------

    prompt = f"""
You are a helpful AI assistant for a retail store.

Answer the user's question using ONLY the information provided in the context.

Rules:
- Do not invent information.
- Do not assume information that is not in the context.
- If the context does not contain the answer,
  say that you don't have enough information.
- Give a concise answer.
- Do not mention filenames or sources in your answer.

CONTEXT:
{context}

USER QUESTION:
{question}
"""

    # -------------------------
    # Generate answer
    # -------------------------

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text, results