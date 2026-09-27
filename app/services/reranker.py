def rerank_documents(
    question,
    documents,
    metadatas,
    top_k=3
):
    """
    Lightweight reranking fallback.

    SentenceTransformer/CrossEncoder is intentionally
    not used because the deployment environment has
    limited memory.

    Qdrant's vector similarity order is preserved.
    """

    ranked_results = []

    for i, document in enumerate(documents):

        ranked_results.append({

            "document": document,

            "metadata": metadatas[i],

            "score": 0.0
        })

    return ranked_results[:top_k]