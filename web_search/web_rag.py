from tavily import TavilyClient
from google import genai
from dotenv import load_dotenv
import os
import time
import re
import html


load_dotenv()


gemini_client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


tavily_client = TavilyClient(
    api_key=os.environ["TAVILY_API_KEY"]
)

def clean_content(content):
    """
    Remove HTML tags and normalize whitespace.
    """

    # Remove HTML tags
    content = re.sub(r"<[^>]+>", " ", content)

    # Decode HTML entities
    content = html.unescape(content)

    # Normalize whitespace
    content = re.sub(r"\s+", " ", content)

    return content.strip()

def process_results(results, top_k=3, max_content_length=3000):

    processed_results = []

    for result in results:

        cleaned_content = clean_content(
            result.get("content", "")
        )

        processed_results.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": cleaned_content[:max_content_length],
            "score": result.get("score", 0),
        })

    # Sort highest relevance first
    processed_results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    # Keep only the best results
    return processed_results[:top_k]

def build_web_context(results):

    context_parts = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"""
SOURCE {index}

Title:
{result["title"]}

URL:
{result["url"]}

Relevance Score:
{result["score"]}

Content:
{result["content"]}
"""
        )

    return "\n\n".join(context_parts)


ALLOWED_DOMAINS = [
    "dmart.in",
    "dmartindia.com",
    "wikipedia.org/wiki/DMart",
    "linkedin.com/company/avenue-supermarts-ltd-dmart",
]


def search_web(query, max_results=5):

    response = tavily_client.search(
        query=query,
        max_results=max_results,
        include_domains=ALLOWED_DOMAINS
    )

    results = []

    for result in response.get("results", []):

        results.append({
    "title": result.get("title", ""),
    "url": result.get("url", ""),
    "content": result.get("content", ""),
    "score": result.get("score", 0),
    "source_type": "approved_web",
})

    return results


def build_web_context(results):

    context_parts = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"""
SOURCE {index}

Title:
{result["title"]}

URL:
{result["url"]}

Content:
{result["content"]}
"""
        )

    return "\n\n".join(context_parts)


def generate_with_retry(prompt, max_retries=3):

    for attempt in range(max_retries):

        try:
            response = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            return response

        except Exception as error:

            error_text = str(error)

            # Quota exceeded
            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

                raise RuntimeError(
                    "Gemini API quota has been exceeded. "
                    "Please wait for the quota to reset or "
                    "check your Gemini API plan and billing."
                )

            # Temporary Gemini server problem
            if "503" in error_text or "UNAVAILABLE" in error_text:

                print(
                    f"\nGemini request failed "
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

                continue

            # Other errors
            raise


def ask_web(question):

    # --------------------------------
    # 1. Search
    # --------------------------------

    raw_results = search_web(
        question,
        max_results=5
    )


    # --------------------------------
    # 2. Process results
    # --------------------------------

    results = process_results(
        raw_results,
        top_k=3,
        max_content_length=3000
    )


    # --------------------------------
    # 2. Build context
    # --------------------------------

    context = build_web_context(results)


    # --------------------------------
    # 3. Create Gemini prompt
    # --------------------------------

    prompt = f"""
You are a helpful AI assistant for DMart.

You may use ONLY the information provided in the approved DMart
web sources below.

These are approved external sources:

- DMart online shopping website
- DMart official corporate website
- DMart Wikipedia page
- DMart LinkedIn company page

Rules:

- Do not use or assume information from other websites.
- Use only the information provided in the search results.
- Do not invent facts.
- If the approved sources do not contain enough information, say so.
- Do not mention internal implementation details.
- Do not mention source numbers such as SOURCE 1 or SOURCE 2.
- Do not include URLs in the answer.

APPROVED WEB SEARCH RESULTS:

{context}

USER QUESTION:

{question}
"""


    # --------------------------------
    # 4. Generate answer
    # --------------------------------

    response = generate_with_retry(prompt)


    # --------------------------------
    # 5. Return answer + structured sources
    # --------------------------------

    return response.text, results


if __name__ == "__main__":

    question = input("Enter your question: ")

    answer, results = ask_web(question)


    print("\n==============================")
    print("AI ANSWER")
    print("==============================")

    print(answer)


    print("\n==============================")
    print("SOURCES")
    print("==============================")


    for index, result in enumerate(results, start=1):

        print("\n------------------------------")

        print(f"Source #{index}")

        print("Title:", result["title"])

        print("URL:", result["url"])

        print("Relevance Score:", result["score"])