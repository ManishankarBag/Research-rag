import os

from openai import OpenAI
from dotenv import load_dotenv

from src.retrieve import retrieve_documents

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

if not os.getenv("GROQ_API_KEY"):
    raise ValueError(
        "GROQ_API_KEY not found. Check your .env file."
    )


def build_context(documents):

    context = ""

    for i, doc in enumerate(documents):

        metadata = doc["metadata"]

        context += f"""

SOURCE {i+1}

Paper:
{metadata["source"]}

Page:
{metadata["page"]}

Content:
{doc["text"]}

-------------------------
"""

    return context


def generate_answer(
    question,
    documents
):

    context = build_context(
        documents
    )

    prompt = f"""
You are a research assistant.

Answer the user's question using ONLY
the research paper excerpts provided below.

Do not use outside knowledge.

If the provided documents do not contain
enough information to answer the question,
say:

"I could not find sufficient information
in the provided research papers."

For every factual claim, cite the relevant
source using [Source X].

Research papers:

{context}

User question:

{question}
"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",
                "content":
                    "You are a careful research assistant."
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    return response.choices[0].message.content


def ask_question(question):

    documents = retrieve_documents(
        question,
        top_k=5
    )

    answer = generate_answer(
        question,
        documents
    )

    return answer, documents



if __name__ == "__main__":

    question = input(
        "Question: "
    )

    answer, sources = ask_question(
        question
    )

    print("\nANSWER")
    print(answer)

    print("\nSOURCES")

    for source in sources:

        print(
            source["metadata"]
        )

