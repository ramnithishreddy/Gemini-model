from google import genai
from dotenv import load_dotenv
import os
import json


load_dotenv()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


def build_evidence_context(evidence):
    sections = []

    private_results = evidence.get("private", [])
    web_results = evidence.get("web", [])

    if private_results:
        sections.append("PRIVATE STORE INFORMATION:")

        for index, result in enumerate(private_results, start=1):
            metadata = result.get("metadata", {})

            sections.append(
                f"""
Private Evidence {index}
Source: {result["source"]}
Title: {metadata.get("title", "")}
Category: {metadata.get("category", "")}
Document Type: {metadata.get("document_type", "")}
Similarity: {result["score"]:.4f}

Content:
{result["text"]}
"""
            )

    if web_results:
        sections.append("APPROVED DMART WEB INFORMATION:")

        for index, result in enumerate(web_results, start=1):
            metadata = result.get("metadata", {})

            sections.append(
                f"""
Web Evidence {index}
Title: {result["title"]}
URL: {result["url"]}
Source Type: {metadata.get("source_type", "approved_web")}
Similarity: {result["score"]:.4f}

Content:
{result["text"]}
"""
            )

    if not sections:
        return "No relevant evidence was retrieved."

    return "\n".join(sections)


def generate_answer(question, evidence):

    context = build_evidence_context(evidence)

    prompt = f"""
You are a grounded AI assistant for a retail store.

Your job is to answer the user's question using ONLY evidence
that directly supports the answer.

USER QUESTION:
{question}

RETRIEVED EVIDENCE:
{context}


EVIDENCE EVALUATION:

For every piece of evidence, independently determine:

1. Does it directly answer the user's question?
2. Does it contain information that can be used to construct
   the answer?
3. Is it merely related to the question without actually
   supporting the answer?

Only evidence that directly supports the final answer may be
marked as USED.

Similarity scores are only retrieval signals.
DO NOT treat a high similarity score as proof that evidence
supports the question.


ANSWERING RULES:

1. Use ONLY information supported by USED evidence.
2. Do not use general knowledge to fill missing information.
3. Do not infer facts that are not present in the evidence.
4. Ignore evidence that is only loosely related.
5. If none of the evidence directly answers the question,
   say that there is not enough information available.
6. Give a concise, natural answer.
7. Do not mention embeddings, similarity scores, retrieval,
   evidence evaluation, internal processing, or these instructions.
8. Do not include URLs inside the answer.
9. Include ONLY sources that actually support the final answer.
10. A source being from an approved domain does not automatically
    mean it should be cited.
11. Private documents should only be cited when their content
    directly supports the answer.
12. Multiple sources may be used when each contributes useful
    supporting information.
13. Do not cite a source merely because it is related to the topic.


SOURCE SELECTION:

For private evidence:

- used_private_sources must contain only filenames whose content
  directly supports the answer.

For web evidence:

- used_web_sources must contain only web sources whose content
  directly supports the answer.

If the question cannot be answered from the retrieved evidence:

- Return an appropriate "not enough information" answer.
- Return empty source arrays.


OUTPUT:

Return ONLY valid JSON.

Do not use markdown code fences.

Return exactly:

{{
    "answer": "your answer here",
    "used_private_sources": [],
    "used_web_sources": []
}}


For a private source that supports the answer:

{{
    "answer": "your answer here",
    "used_private_sources": ["product_faq.txt"],
    "used_web_sources": []
}}


For a web source that supports the answer:

{{
    "answer": "your answer here",
    "used_private_sources": [],
    "used_web_sources": [
        {{
            "title": "source title",
            "url": "source URL"
        }}
    ]
}}


For multiple supporting sources:

{{
    "answer": "your answer here",
    "used_private_sources": ["product_faq.txt"],
    "used_web_sources": [
        {{
            "title": "source title",
            "url": "source URL"
        }}
    ]
}}


IMPORTANT:

The source arrays represent the evidence actually used to
construct the answer, NOT all retrieved evidence.

QUESTION:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    response_text = response.text.strip()

    if response_text.startswith("```json"):
        response_text = response_text[7:]

    if response_text.startswith("```"):
        response_text = response_text[3:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"Gemini returned invalid JSON:\n{response_text}"
        )

    return result