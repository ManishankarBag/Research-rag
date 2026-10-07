import chromadb

from sentence_transformers import SentenceTransformer


CHROMA_PATH = "chroma_db"


embedding_model = SentenceTransformer(
    "BAAI/bge-small-en-v1.5"
)


client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


collection = client.get_collection(
    name="research_papers"
)


def retrieve_documents(
    query,
    top_k=5
):

    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    )[0]

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],

        n_results=top_k
    )

    documents = []

    for i in range(
        len(results["documents"][0])
    ):

        documents.append({

            "text":
                results["documents"][0][i],

            "metadata":
                results["metadatas"][0][i],

            "distance":
                results["distances"][0][i]
        })

    return documents


if __name__ == "__main__":

    query = input(
        "Enter your question: "
    )

    results = retrieve_documents(query)

    for i, result in enumerate(results):

        print(
            f"\n--- Result {i+1} ---"
        )

        print(
            result["metadata"]
        )

        print(
            result["text"][:1000]
        )