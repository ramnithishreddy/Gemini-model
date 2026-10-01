def chunk_document(document, chunk_size=500, overlap=100):

    words = document["text"].split()

    chunks = []

    start = 0
    chunk_index = 0

    while start < len(words):

        end = start + chunk_size

        chunk_text = " ".join(words[start:end])

        chunks.append({
            "chunk_id": f'{document["source"]}_chunk_{chunk_index}',
            "source": document["source"],
            "chunk_index": chunk_index,
            "text": chunk_text,
            "metadata": document["metadata"]
        })

        start += chunk_size - overlap
        chunk_index += 1

    return chunks