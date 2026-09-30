import re


GREETING_WORDS = {
    "hi",
    "hello",
    "hey",
    "hey mate",
    "hi mate",
    "hello mate",
    "good morning",
    "good afternoon",
    "good evening"
}


CASUAL_RESPONSES = {
    "hi": "Hello! How can I help you with your document?",
    "hello": "Hello! How can I help you with your document?",
    "hey": "Hey! How can I help you with your document?",
    "hey mate": "Hey mate! How can I help you with your document?",
    "hi mate": "Hi mate! How can I help you with your document?",
    "hello mate": "Hello mate! How can I help you with your document?",
    "good morning": "Good morning! How can I help you with your document?",
    "good afternoon": "Good afternoon! How can I help you with your document?",
    "good evening": "Good evening! How can I help you with your document?"
}


def normalize_text(text):

    text = text.lower().strip()

    text = re.sub(
        r"[!?.,]+$",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


def classify_intent(question):

    normalized_question = normalize_text(
        question
    )

    # ====================================
    # 1. Exact greetings
    # ====================================

    if normalized_question in GREETING_WORDS:
        return "casual"


    # ====================================
    # 2. Casual conversation
    # ====================================

    casual_phrases = [
        "how are you",
        "how are you doing",
        "how are things",
        "what's up",
        "whats up",
        "thank you",
        "thanks",
        "thank u",
        "bye",
        "goodbye",
        "see you",
        "see ya",
        "ok",
        "okay",
        "ok mate",
        "okay mate"
    ]

    for phrase in casual_phrases:

        if normalized_question == phrase:
            return "casual"


    # ====================================
    # 3. Identity questions
    # ====================================

    identity_phrases = [
        "who are you",
        "what are you",
        "what is your name",
        "whats your name",
        "what technology are you using",
        "what technologies are you using",
        "what tech stack are you using",
        "what is your tech stack",
        "what stack are you using",
        "what are you built with",
        "what were you built with",
        "what model are you",
        "which model are you",
        "what ai model are you",
        "which ai model are you",
        "how do you work",
        "how does this work",
        "how do you answer",
        "what can you do",
        "what do you do",
        "what are your capabilities"
    ]

    for phrase in identity_phrases:

        if normalized_question == phrase:
            return "identity"


    # ====================================
    # 4. Document question
    # ====================================

    return "document"


def get_casual_response(question):

    normalized_question = normalize_text(
        question
    )


    # Greetings

    if normalized_question in CASUAL_RESPONSES:

        return CASUAL_RESPONSES[
            normalized_question
        ]


    # How are you?

    if normalized_question in [
        "how are you",
        "how are you doing",
        "how are things"
    ]:

        return (
            "I'm doing great! "
            "I'm ready to help you with your document."
        )


    # Thanks

    if normalized_question in [
        "thank you",
        "thanks",
        "thank u"
    ]:

        return (
            "You're welcome! "
            "Feel free to ask me anything about your document."
        )


    # Goodbye

    if normalized_question in [
        "bye",
        "goodbye",
        "see you",
        "see ya"
    ]:

        return (
            "Goodbye! "
            "Feel free to come back if you need help "
            "with your document."
        )


    # OK

    if normalized_question in [
        "ok",
        "okay",
        "ok mate",
        "okay mate"
    ]:

        return (
            "Sure! "
            "You can ask me anything about your document."
        )


    return (
        "Sure! "
        "How can I help you with your document?"
    )