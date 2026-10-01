from ingestion.embedder import create_embedding
from rag.similarity import cosine_similarity
from rag.vector_store import load_vectors
from web_search.search import search_web
from web_search.web_rag import clean_content


PRIVATE_MIN_SCORE = 0.55
WEB_MIN_SCORE = 0.55


def retrieve_private(question_embedding, top_k=3):
    """
    Retrieve semantically relevant private documents.
    Metadata is preserved for evidence selection and source display.
    """

    chunks = load_vectors()

    results = []

    for chunk in chunks:

        score = cosine_similarity(
            question_embedding,
            chunk["embedding"]
        )

        results.append({
            "type": "private",
            "source": chunk["source"],
            "text": chunk["text"],
            "score": score,
            "metadata": chunk.get("metadata", {})
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return [
        result
        for result in results
        if result["score"] >= PRIVATE_MIN_SCORE
    ][:top_k]


def is_dmart_relevant(result):
    """
    Keep web results that are actually about DMart / Avenue Supermarts.
    """

    text = " ".join([
        result.get("title", ""),
        result.get("text", ""),
        result.get("url", "")
    ]).lower()

    dmart_indicators = [
        "dmart",
        "d-mart",
        "avenue supermarts",
        "avenue supermarkets"
    ]

    return any(
        indicator in text
        for indicator in dmart_indicators
    )


def retrieve_web(question, question_embedding, max_results=5, top_k=3):
    """
    Search approved web sources and semantically rerank them
    using the same embedding model as private documents.
    """

    web_results = search_web(
        question,
        max_results=max_results
    )

    results = []

    seen_urls = set()
    seen_content = set()

    for result in web_results:

        url = result.get("url", "")

        content = clean_content(
            result.get("content", "")
        )

        if not content:
            continue

        candidate = {
            "title": result.get("title", ""),
            "url": url,
            "text": content
        }

        if not is_dmart_relevant(candidate):
            continue

        if url in seen_urls:
            continue

        content_key = content[:1000].lower()

        if content_key in seen_content:
            continue

        seen_urls.add(url)
        seen_content.add(content_key)

        content_embedding = create_embedding(content)

        score = cosine_similarity(
            question_embedding,
            content_embedding
        )

        results.append({
            "type": "web",
            "title": candidate["title"],
            "url": url,
            "text": content,
            "score": score,
            "metadata": {
                "source_type": "approved_web",
                "title": candidate["title"],
                "url": url
            }
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return [
        result
        for result in results
        if result["score"] >= WEB_MIN_SCORE
    ][:top_k]


def select_evidence(private_results, web_results):
    """
    Select evidence based on relevance.

    Results below the minimum relevance threshold have already
    been removed during retrieval.

    The strongest result from each source is selected.
    Additional results are only kept when they are close to
    the strongest result.
    """

    def select_from_source(results):

        if not results:
            return []

        strongest = results[0]

        selected = [strongest]

        for result in results[1:]:

            if result["score"] >= strongest["score"] * 0.90:
                selected.append(result)

        return selected

    private_evidence = select_from_source(
        private_results
    )

    web_evidence = select_from_source(
        web_results
    )

    return private_evidence, web_evidence


def retrieve_evidence(question):
    """
    Retrieve evidence from both private and approved web sources.
    """

    question_embedding = create_embedding(question)

    private_results = retrieve_private(
        question_embedding=question_embedding
    )

    web_results = retrieve_web(
        question=question,
        question_embedding=question_embedding
    )

    private_evidence, web_evidence = select_evidence(
        private_results,
        web_results
    )

    return {
        "private": private_evidence,
        "web": web_evidence
    }