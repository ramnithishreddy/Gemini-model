from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".txt"
}


DOCUMENT_METADATA = {
    "product_faq.txt": {
        "category": "store_information",
        "document_type": "product_faq",
        "title": "Product FAQ",
        "source_type": "private"
    },

    "return_policy.txt": {
        "category": "policy",
        "document_type": "return_policy",
        "title": "Retail Store Return Policy",
        "source_type": "private"
    },

    "store_info.txt": {
        "category": "store_information",
        "document_type": "store_information",
        "title": "Store Information",
        "source_type": "private"
    }
}


def load_text_file(file_path):
    path = Path(file_path)

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def load_documents(directory="documents"):

    documents = []

    directory_path = Path(directory)

    for file_path in directory_path.iterdir():

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = load_text_file(file_path)

        metadata = DOCUMENT_METADATA.get(
            file_path.name,
            {
                "category": "general",
                "document_type": "text",
                "title": file_path.stem,
                "source_type": "private"
            }
        )

        documents.append({
            "source": file_path.name,
            "path": str(file_path),
            "text": text,
            "metadata": metadata
        })

    return documents