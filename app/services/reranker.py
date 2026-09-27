from sentence_transformers import CrossEncoder


model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_documents(question, documents, metadatas, top_k=3):

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