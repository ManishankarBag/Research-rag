# import os
# import hashlib

# import fitz
# import chromadb

# from sentence_transformers import SentenceTransformer


# PAPERS_DIR = "data/papers"
# CHROMA_PATH = "chroma_db"


# # -----------------------------
# # Embedding model
# # -----------------------------

# embedding_model = SentenceTransformer(
#     "BAAI/bge-small-en-v1.5"
# )


# # -----------------------------
# # ChromaDB
# # -----------------------------

# client = chromadb.PersistentClient(
#     path=CHROMA_PATH
# )

# collection = client.get_or_create_collection(
#     name="research_papers"
# )


# # -----------------------------
# # PDF extraction
# # -----------------------------

# def extract_pdf(pdf_path):

#     doc = fitz.open(pdf_path)

#     pages = []

#     for page_number, page in enumerate(doc, start=1):

#         text = page.get_text("text")

#         if text.strip():

#             pages.append({
#                 "text": text,
#                 "page": page_number
#             })

#     doc.close()

#     return pages


# # -----------------------------
# # Chunking
# # -----------------------------

# def chunk_text(
#     text,
#     chunk_size=1000,
#     overlap=150
# ):

#     words = text.split()

#     chunks = []

#     start = 0

#     while start < len(words):

#         end = start + chunk_size

#         chunk = " ".join(words[start:end])

#         if chunk.strip():

#             chunks.append(chunk)

#         start += chunk_size - overlap

#     return chunks


# # -----------------------------
# # File hash
# # -----------------------------

# def get_file_hash(filepath):

#     sha256 = hashlib.sha256()

#     with open(filepath, "rb") as f:

#         while True:

#             data = f.read(8192)

#             if not data:
#                 break

#             sha256.update(data)

#     return sha256.hexdigest()


# # -----------------------------
# # Process one PDF
# # -----------------------------

# def process_pdf(pdf_path):

#     filename = os.path.basename(pdf_path)

#     file_hash = get_file_hash(pdf_path)

#     pages = extract_pdf(pdf_path)

#     documents = []

#     for page_data in pages:

#         chunks = chunk_text(
#             page_data["text"]
#         )

#         for chunk_number, chunk in enumerate(chunks):

#             document_id = (
#                 f"{file_hash}_"
#                 f"{page_data['page']}_"
#                 f"{chunk_number}"
#             )

#             documents.append({
#                 "id": document_id,
#                 "text": chunk,
#                 "metadata": {
#                     "source": filename,
#                     "page": page_data["page"],
#                     "chunk": chunk_number,
#                     "file_hash": file_hash
#                 }
#             })

#     return documents


# # -----------------------------
# # Ingest PDF
# # -----------------------------

# def ingest_pdf(pdf_path):

#     documents = process_pdf(pdf_path)

#     if not documents:

#         print(
#             f"No text found: {pdf_path}"
#         )

#         return

#     texts = [
#         doc["text"]
#         for doc in documents
#     ]

#     embeddings = embedding_model.encode(
#         texts,
#         normalize_embeddings=True
#     )

#     collection.upsert(
#         ids=[
#             doc["id"]
#             for doc in documents
#         ],

#         documents=texts,

#         embeddings=embeddings.tolist(),

#         metadatas=[
#             doc["metadata"]
#             for doc in documents
#         ]
#     )

#     print(
#         f"Ingested: "
#         f"{os.path.basename(pdf_path)} "
#         f"({len(documents)} chunks)"
#     )


# # -----------------------------
# # Main
# # -----------------------------

# if __name__ == "__main__":

#     pdf_files = [
#         f
#         for f in os.listdir(PAPERS_DIR)
#         if f.lower().endswith(".pdf")
#     ]

#     print(
#         f"Found {len(pdf_files)} PDFs"
#     )

#     for filename in pdf_files:

#         pdf_path = os.path.join(
#             PAPERS_DIR,
#             filename
#         )

#         ingest_pdf(pdf_path)

#     print("\nTotal chunks:")

#     print(collection.count())
import os
import hashlib

import fitz
import chromadb

from sentence_transformers import SentenceTransformer


PAPERS_DIR = "data/papers"
CHROMA_PATH = "chroma_db"

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"


# -----------------------------
# Embedding model
# -----------------------------

_embedding_model = None


def get_embedding_model():

    global _embedding_model

    if _embedding_model is None:

        print("Loading embedding model...")

        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )

        print("Embedding model loaded.")

    return _embedding_model


# -----------------------------
# ChromaDB
# -----------------------------

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_or_create_collection(
    name="research_papers"
)


# -----------------------------
# PDF extraction
# -----------------------------

def extract_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(doc, start=1):

        text = page.get_text("text")

        if text.strip():

            pages.append({
                "text": text,
                "page": page_number
            })

    doc.close()

    return pages


# -----------------------------
# Chunking
# -----------------------------

def chunk_text(
    text,
    chunk_size=1000,
    overlap=150
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():

            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# -----------------------------
# File hash
# -----------------------------

def get_file_hash(filepath):

    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:

        while True:

            data = f.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


# -----------------------------
# Process one PDF
# -----------------------------

def process_pdf(pdf_path):

    filename = os.path.basename(pdf_path)

    file_hash = get_file_hash(pdf_path)

    pages = extract_pdf(pdf_path)

    documents = []

    for page_data in pages:

        chunks = chunk_text(
            page_data["text"]
        )

        for chunk_number, chunk in enumerate(chunks):

            document_id = (
                f"{file_hash}_"
                f"{page_data['page']}_"
                f"{chunk_number}"
            )

            documents.append({
                "id": document_id,
                "text": chunk,
                "metadata": {
                    "source": filename,
                    "page": page_data["page"],
                    "chunk": chunk_number,
                    "file_hash": file_hash
                }
            })

    return documents


# -----------------------------
# Ingest PDF
# -----------------------------

def ingest_pdf(pdf_path):

    print(
        f"Processing: {os.path.basename(pdf_path)}"
    )

    documents = process_pdf(pdf_path)

    if not documents:

        print(
            f"No text found: {pdf_path}"
        )

        return 0

    texts = [
        doc["text"]
        for doc in documents
    ]

    # Load model only when actually needed
    embedding_model = get_embedding_model()

    embeddings = embedding_model.encode(
        texts,
        normalize_embeddings=True
    )

    collection.upsert(
        ids=[
            doc["id"]
            for doc in documents
        ],

        documents=texts,

        embeddings=embeddings.tolist(),

        metadatas=[
            doc["metadata"]
            for doc in documents
        ]
    )

    print(
        f"Ingested: "
        f"{os.path.basename(pdf_path)} "
        f"({len(documents)} chunks)"
    )

    return len(documents)


# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":

    pdf_files = [
        f
        for f in os.listdir(PAPERS_DIR)
        if f.lower().endswith(".pdf")
    ]

    print(
        f"Found {len(pdf_files)} PDFs"
    )

    total_chunks = 0

    for filename in pdf_files:

        pdf_path = os.path.join(
            PAPERS_DIR,
            filename
        )

        total_chunks += ingest_pdf(
            pdf_path
        )

    print("\nTotal chunks:")

    print(collection.count())