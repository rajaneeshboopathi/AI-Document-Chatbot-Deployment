from app.services.embeddings import generate_embedding
from app.services.vector_store import search_chunks
from app.services.llm import generate_answer
from app.services.reranker import rerank_documents


def answer_question(question, chat_id):

    # Generate embedding for the user's question
    query_embedding = generate_embedding(question)

    # Search the vector database
    results = search_chunks(
        query_embedding,
        chat_id,
        top_k=10
    )

    # Check whether any documents were found
    if (
        not results
        or not results.get("documents")
        or not results["documents"][0]
    ):
        return {
            "answer": (
                "I could not find any uploaded document "
                "for this chat. Please upload a document first."
            ),
            "sources": []
        }

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Rerank the retrieved documents
    ranked_results = rerank_documents(
        question,
        documents,
        metadatas,
        top_k=5
    )

    # Check whether reranking returned anything
    if not ranked_results:
        return {
            "answer": (
                "I could not find relevant information "
                "in the uploaded document."
            ),
            "sources": []
        }

    # Build context for the LLM
    context_parts = []

    for result in ranked_results:

        document = result["metadata"]["document"]
        page = result["metadata"]["page"]
        text = result["document"]

        context_parts.append(
            f"Source: {document}, Page: {page}\n"
            f"Content: {text}"
        )

    context = "\n\n".join(context_parts)

    # Generate final answer using the retrieved context
    answer = generate_answer(
        question,
        context
    )

    # Return unique source documents/pages
    unique_sources = []

    for result in ranked_results:

        source = {
            "document": result["metadata"]["document"],
            "page": result["metadata"]["page"]
        }

        if source not in unique_sources:
            unique_sources.append(source)

    return {
        "answer": answer,
        "sources": unique_sources
    }