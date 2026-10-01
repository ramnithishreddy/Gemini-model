import re


PRIVATE_KEYWORDS = [
    "return policy",
    "return",
    "refund policy",
    "store policy",
    "store timings",
    "store timing",
    "opening time",
    "closing time",
    "what time does the store open",
    "what time does the store close",
    "grocery section",
    "personal care section",
    "home care section",
    "electronics section",
    "clothing section",
    "where can i find",
    "where is",
    "basmati rice",
    "aashirvaad atta",
    "surf excel",
    "dove shampoo",
    "product faq",
    "store information",
]


WEB_KEYWORDS = [
    "latest",
    "current",
    "today",
    "today's",
    "recent",
    "recently",
    "news",
    "announcement",
    "announced",
    "company",
    "corporate",
    "about dmart",
    "about dmarts",
    "dmart history",
    "dmart website",
    "official website",
    "linkedin",
    "wikipedia",
]


BUSINESS_KEYWORDS = [
    "stock",
    "in stock",
    "inventory",
    "available in stock",
    "sku",
    "product price",
    "price of",
    "how much does",
    "cost of",
    "order",
    "my order",
    "cart",
    "quantity",
    "how many units",
]


def contains_keyword(question, keywords):
    question = question.lower()

    return any(
        keyword in question
        for keyword in keywords
    )


def route_question(question):
    """
    Decide which knowledge source should answer the question.

    Returns:
        private
        web
        business
    """

    question = question.strip().lower()

    business_match = contains_keyword(
        question,
        BUSINESS_KEYWORDS
    )

    web_match = contains_keyword(
        question,
        WEB_KEYWORDS
    )

    private_match = contains_keyword(
        question,
        PRIVATE_KEYWORDS
    )

    # Business data has highest priority.
    if business_match:
        return "business"

    # Explicit current/web/company questions.
    if web_match:
        return "web"

    # Questions matching our private documents.
    if private_match:
        return "private"

    # Default to private knowledge.
    return "private"