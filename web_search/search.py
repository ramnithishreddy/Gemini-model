from tavily import TavilyClient
from dotenv import load_dotenv
import os


load_dotenv()


ALLOWED_DOMAINS = [
    "dmart.in",
    "dmartindia.com",
    "wikipedia.org",
    "linkedin.com",
]


client = TavilyClient(
    api_key=os.environ["TAVILY_API_KEY"]
)


def search_web(query, max_results=5):
    response = client.search(
        query=query,
        max_results=max_results,
        include_domains=ALLOWED_DOMAINS
    )

    normalized_results = []

    for result in response.get("results", []):
        normalized_results.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
            "score": result.get("score", 0),
        })

    return normalized_results


if __name__ == "__main__":

    query = input("Enter your search query: ")

    results = search_web(query)

    print("\n==============================")
    print("WEB SEARCH RESULTS")
    print("==============================")

    for index, result in enumerate(results, start=1):

        print("\n------------------------------")
        print(f"Result #{index}")

        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Score:", result["score"])

        print("\nContent:")
        print(result["content"])