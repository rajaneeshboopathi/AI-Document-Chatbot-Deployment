import re


# ---------------------------------------------------------
# Greeting words
# ---------------------------------------------------------

GREETING_WORDS = {
    "hi",
    "hello",
    "hey",
    "hey mate",
    "hi mate",
    "hello mate",
    "good morning",
    "good afternoon",
    "good evening",
}


# ---------------------------------------------------------
# Casual conversation responses
# ---------------------------------------------------------

CASUAL_RESPONSES = {
    "hi": "Hi! How can I help you with your document?",
    "hello": "Hello! How can I help you with your document?",
    "hey": "Hey! How can I help you with your document?",
    "hey mate": "Hey mate! How can I help you with your document?",
    "hi mate": "Hi mate! How can I help you with your document?",
    "hello mate": "Hello mate! How can I help you with your document?",
    "good morning": "Good morning! How can I help you with your document?",
    "good afternoon": "Good afternoon! How can I help you with your document?",
    "good evening": "Good evening! How can I help you with your document?",
    "how are you": "I'm doing great! How can I help you with your document?",
    "how are you doing": "I'm doing great! How can I help you with your document?",
    "how are things": "I'm doing great! How can I help you with your document?",
    "what's up": "I'm here and ready to help! What would you like to know?",
    "whats up": "I'm here and ready to help! What would you like to know?",
    "thank you": "You're welcome!",
    "thanks": "You're welcome!",
    "thank u": "You're welcome!",
    "bye": "Goodbye! Feel free to come back if you have more questions.",
    "goodbye": "Goodbye! Feel free to come back if you have more questions.",
    "see you": "See you! Feel free to come back anytime.",
    "see ya": "See you! Feel free to come back anytime.",
    "ok": "Sure!",
    "okay": "Sure!",
    "ok mate": "Sure mate!",
    "okay mate": "Sure mate!",
}


# ---------------------------------------------------------
# Normalize user input
# ---------------------------------------------------------

def normalize_text(text):
    """
    Normalize user input so that small differences in
    punctuation, spacing, and capitalization do not affect
    intent detection.

    Examples:

        "Who are you?"
        "who are you ?"
        "WHO ARE YOU!!!"
        "who are you"

    All become:

        "who are you"
    """

    if not text:
        return ""

    text = text.lower().strip()

    # Replace punctuation/symbols with spaces.
    #
    # This handles:
    # "who are you?"
    # "who are you ?"
    # "who are you!!!"
    # "what technology do you use?"
    #
    # All punctuation becomes whitespace.
    text = re.sub(r"[^\w\s]", " ", text)

    # Remove extra spaces.
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ---------------------------------------------------------
# Intent classification
# ---------------------------------------------------------

def classify_intent(question):
    """
    Classify the user's question into:

        casual
        identity
        document

    Anything that is not clearly casual or identity-related
    is treated as a document question.
    """

    normalized_question = normalize_text(question)

    # Empty input
    if not normalized_question:
        return "document"

    # -----------------------------------------------------
    # Casual greetings
    # -----------------------------------------------------

    if normalized_question in GREETING_WORDS:
        return "casual"

    # -----------------------------------------------------
    # Casual conversation
    # -----------------------------------------------------

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
        "okay mate",
    ]

    for phrase in casual_phrases:
        if normalized_question == normalize_text(phrase):
            return "casual"

    # -----------------------------------------------------
    # Identity / chatbot questions
    # -----------------------------------------------------

    identity_phrases = [

        # ---------------------------------------------
        # Who is the assistant?
        # ---------------------------------------------

        "who are you",
        "what are you",
        "what is your name",
        "whats your name",
        "your name",

        # ---------------------------------------------
        # Technology / stack
        # ---------------------------------------------

        "what technology are you using",
        "what technologies are you using",
        "what technology do you use",
        "what technologies do you use",
        "what tech do you use",
        "what tech are you using",
        "what tech stack are you using",
        "what is your tech stack",
        "what stack are you using",
        "what are you built with",
        "what were you built with",
        "what technology did you use",
        "what technologies did you use",

        # ---------------------------------------------
        # AI model
        # ---------------------------------------------

        "what model are you",
        "which model are you",
        "what ai model are you",
        "which ai model are you",

        # ---------------------------------------------
        # How the assistant works
        # ---------------------------------------------

        "how do you work",
        "how does this work",
        "how do you answer",

        # ---------------------------------------------
        # Capabilities
        # ---------------------------------------------

        "what can you do",
        "what do you do",
        "what are your capabilities",
    ]

    normalized_identity_phrases = {
        normalize_text(phrase)
        for phrase in identity_phrases
    }

    if normalized_question in normalized_identity_phrases:
        return "identity"

    # -----------------------------------------------------
    # Everything else = document question
    # -----------------------------------------------------

    return "document"


# ---------------------------------------------------------
# Casual response
# ---------------------------------------------------------

def get_casual_response(question):
    """
    Return a predefined response for casual conversation.
    """

    normalized_question = normalize_text(question)

    return CASUAL_RESPONSES.get(
        normalized_question,
        "Sure! How can I help you with your document?"
    )