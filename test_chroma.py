import chromadb
from pathlib import Path

path = Path("./chroma_test").resolve()
client = chromadb.PersistentClient(path=str(path))
collection = client.get_or_create_collection("test_collection")
print("SUCCESS: ChromaDB initialized")
