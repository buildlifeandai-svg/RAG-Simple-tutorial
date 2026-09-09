import os
import numpy as np
from openai import OpenAI

client = OpenAI(

    api_key=os.environ["OPENAI_API_KEY"]

)
#Load employee handbook
with open("employee_handbook.txt", "r") as file:
    text = file.read()

# Each policy is separated by a blank line
chunks = text.split("\n\n")
#
print(chunks)

#3. Split the handbook into chunks
#
# For this tiny demo, every policy is separated
# by a blank line.
# ---------------------------------------------------------

chunks = text.split("\n\n")

print("\n--- DOCUMENT CHUNKS ---")

for i, chunk in enumerate(chunks):
    print(f"\nChunk {i + 1}:")
    print(chunk)

# ---------------------------------------------------------
# 4. Create embeddings
# ---------------------------------------------------------

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


print("\nCreating embeddings for document chunks...")

chunk_embeddings = [
    get_embedding(chunk)
    for chunk in chunks
]

print(f"Created {len(chunk_embeddings)} embeddings.")

# ---------------------------------------------------------
# 5. Cosine similarity
# ---------------------------------------------------------

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )

# ---------------------------------------------------------
# 6. Retriever
# ---------------------------------------------------------

def retrieve(question, top_k=2):

    # Embed the user's question
    question_embedding = get_embedding(question)

    # Compare the question with every document chunk
    similarities = [
        cosine_similarity(
            question_embedding,
            chunk_embedding
        )
        for chunk_embedding in chunk_embeddings
    ]

    # Sort chunks from highest similarity to lowest
    ranked_indices = np.argsort(similarities)[::-1]

    # Return the top K chunks
    results = []

    for i in ranked_indices[:top_k]:
        results.append({
            "text": chunks[i],
            "score": similarities[i]
        })

    return results

# ---------------------------------------------------------
# 7. Ask the LLM using retrieved context
# ---------------------------------------------------------

def ask_rag(question, top_k=2):

    print("\n========================================")
    print("QUESTION")
    print("========================================")
    print(question)

    # RETRIEVAL
    results = retrieve(
        question,
        top_k=top_k
    )

    print("\n========================================")
    print("RETRIEVED CHUNKS")
    print("========================================")

    for result in results:
        print(
            f"\nSimilarity: {result['score']:.4f}"
        )
        print(result["text"])

    # AUGMENTATION
    context = "\n\n".join(
        result["text"]
        for result in results
    )

    prompt = f"""




Context:
{context}

Question:
{question}

Answer:
"""

    # GENERATION
    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    answer = response.output_text

    print("\n========================================")
    print("FINAL ANSWER")
    print("========================================")
    print(answer)

    return answer

# # 8. TEST 1
# #
# # Notice that the handbook does NOT literally contain
# # the phrase "machine learning training."
# #
# # Semantic retrieval should still find Learning Benefit.
# # ---------------------------------------------------------
#
# question = (
#     "How much money can I spend "
#     "on machine learning training every year?"
# )
#
# ask_rag(
#     question,
#     top_k=2
# )


# ---------------------------------------------------------
# 9. TEST 2 — BREAK THE RAG SYSTEM
#
# There is no lunch policy.
#
# But top_k=2 still forces the retriever to return
# the two highest-scoring chunks.
#
# Highest similarity does NOT necessarily mean relevant.
# ---------------------------------------------------------

question = (
    "How many free lunches do employees "
    "receive every month?"
)

ask_rag(
    question,
    top_k=2
)




