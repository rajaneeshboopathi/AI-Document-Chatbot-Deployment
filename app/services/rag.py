from app.services.embeddings import generate_embedding
from app.services.vector_store import search_chunks
from app.services.llm import generate_answer
from app.services.reranker import rerank_documents
from app.services.query_analyzer import analyze_query


def answer_question(question, chat_id):
    """
    Main RAG pipeline.

    Flow:

        Question
            ↓
        Query Analyzer
            ↓
        Embedding
            ↓
        Qdrant retrieval
            ↓
        Optional page filtering
            ↓
        Reranking
            ↓
        Gemini
            ↓
        Answer + Sources
    """

    # --------------------------------------------------------
    # 1. Analyze the user's question
    # --------------------------------------------------------

    query_info = analyze_query(question)

    search_query = query_info["search_query"]
    page_start = query_info["page_start"]
    page_end = query_info["page_end"]
    query_type = query_info["query_type"]

    # If removing the page reference leaves an empty query,
    # use the original question for embedding.
    if not search_query:
        search_query = question

    print("Query analysis:")
    print(f"  Original: {question}")
    print(f"  Search query: {search_query}")
    print(f"  Page start: {page_start}")
    print(f"  Page end: {page_end}")
    print(f"  Query type: {query_type}")

    # --------------------------------------------------------
    # 2. Generate embedding from the cleaned query
    # --------------------------------------------------------

    query_embedding = generate_embedding(search_query)

    # --------------------------------------------------------
    # 3. Search Qdrant
    #
    # If pages were detected:
    #
    #   chat_id + page range
    #
    # Otherwise:
    #
    #   chat_id only
    # --------------------------------------------------------

    results = search_chunks(
        query_embedding=query_embedding,
        chat_id=chat_id,
        top_k=10,
        page_start=page_start,
        page_end=page_end,
    )

    # --------------------------------------------------------
    # 4. Check whether anything was retrieved
    # --------------------------------------------------------

    if (
        not results
        or not results.get("documents")
        or not results["documents"][0]
    ):
        return {
            "answer": (
                "I could not find relevant information "
                "in the uploaded document."
            ),
            "sources": [],
        }

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # --------------------------------------------------------
    # 5. Rerank retrieved chunks
    # --------------------------------------------------------

    ranked_results = rerank_documents(
        question,
        documents,
        metadatas,
        top_k=5,
    )

    if not ranked_results:
        return {
            "answer": (
                "I could not find relevant information "
                "in the uploaded document."
            ),
            "sources": [],
        }

    # --------------------------------------------------------
    # 6. Build context for Gemini
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 7. Generate final answer
    # --------------------------------------------------------

    answer = generate_answer(
        question,
        context,
    )

    # --------------------------------------------------------
    # 8. Build unique sources
    # --------------------------------------------------------

    unique_sources = []

    for result in ranked_results:
        source = {
            "document": result["metadata"]["document"],
            "page": result["metadata"]["page"],
        }

        if source not in unique_sources:
            unique_sources.append(source)

    return {
        "answer": answer,
        "sources": unique_sources,
    }