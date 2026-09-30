def get_identity_response(question):
    """
    Returns a direct response to questions about the chatbot itself.
    """

    text = question.lower().strip()

    # --------------------------------------------------------
    # Who are you?
    # --------------------------------------------------------

    if (
        "who are you" in text
        or "what are you" in text
        or "what is your name" in text
        or "your name" in text
    ):
        return (
            "I'm an AI document assistant built to answer "
            "questions from your uploaded documents."
        )

    # --------------------------------------------------------
    # What technology are you using?
    # --------------------------------------------------------

    if (
        "what technology" in text
        or "what technologies" in text
        or "what tech stack" in text
        or "what stack" in text
        or "what are you built with" in text
        or "what were you built with" in text
    ):
        return (
            "I'm built using Python, FastAPI, Qdrant, "
            "Gemini embeddings, Gemini models, and a RAG "
            "pipeline for document-based question answering."
        )

    # --------------------------------------------------------
    # What model are you?
    # --------------------------------------------------------

    if (
        "what model are you" in text
        or "which model are you" in text
        or "what ai model" in text
        or "which ai model" in text
    ):
        return (
            "I use Google's Gemini models for answer generation, "
            "with automatic fallback between supported Gemini models "
            "when necessary."
        )

    # --------------------------------------------------------
    # How do you work?
    # --------------------------------------------------------

    if (
        "how do you work" in text
        or "how does this work" in text
        or "how do you answer" in text
    ):
        return (
            "I use retrieval-augmented generation. I search the "
            "uploaded document for relevant content, retrieve the "
            "matching sections, and use that context to generate "
            "the answer."
        )

    # --------------------------------------------------------
    # What can you do?
    # --------------------------------------------------------

    if (
        "what can you do" in text
        or "what do you do" in text
        or "what are your capabilities" in text
    ):
        return (
            "I can analyze uploaded PDF, TXT, and DOCX documents, "
            "answer questions about their contents, maintain chat "
            "history, and provide the document pages used as sources."
        )

    return (
        "I'm an AI document assistant designed to answer "
        "questions using your uploaded documents."
    )