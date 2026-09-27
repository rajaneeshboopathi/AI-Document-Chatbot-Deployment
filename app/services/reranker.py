import os


USE_RERANKER = os.getenv("USE_RERANKER", "true").lower() == "true"

model = None

if USE_RERANKER:
    from sentence_transformers import CrossEncoder

    model = CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )


def rerank_documents(question, documents, metadatas, top_k=3):

    # If reranking is disabled, keep the original
    # vector-search order.
    if not USE_RERANKER:
        ranked_results = []

        for i, document in enumerate(documents):
            ranked_results.append({
                "document": document,
                "metadata": metadatas[i],
                "score": 0.0
            })

        return ranked_results[:top_k]

    pairs = []

    for document in documents:
        pairs.append([
            question,
            document
        ])

    scores = model.predict(pairs)

    ranked_results = []

    for i, score in enumerate(scores):

        ranked_results.append({
            "document": documents[i],
            "metadata": metadatas[i],
            "score": float(score)
        })

    ranked_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked_results[:top_k]