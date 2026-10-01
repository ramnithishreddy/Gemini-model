import chromadb
from chromadb.config import Settings

print("1. Starting Chroma...")

settings = Settings(
    anonymized_telemetry=False,
    chroma_api_impl="chromadb.api.segment.SegmentAPI"
)

client = chromadb.Client(settings)

print("2. Chroma client created")

collection = client.get_or_create_collection(
    name="retail_test"
)

print("3. Collection created")

documents = [
    "India Gate Basmati Rice is available in aisle A-15.",
    "Aashirvaad Atta is available in aisle A-12.",
    "Surf Excel Matic is available in aisle B-05.",
    "Dove Shampoo is available in aisle C-08."
]

ids = [
    "P001",
    "P002",
    "P003",
    "P004"
]

print("4. About to add documents...")

collection.add(
    ids=ids,
    documents=documents
)

print("5. Documents added")

print("6. About to search...")

results = collection.query(
    query_texts=["Where can I find basmati rice?"],
    n_results=2
)

print("7. Search completed")

print("\nResults:")
print(results)

print("\n8. Finished")