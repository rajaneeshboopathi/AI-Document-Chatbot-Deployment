import logging
import os


# Create logs folder if it doesn't exist
os.makedirs("logs", exist_ok=True)


# Create logger
logger = logging.getLogger("ai_document_chatbot")

logger.setLevel(logging.INFO)


# Prevent duplicate handlers if FastAPI reloads
if not logger.handlers:

    # Save logs to a file
    file_handler = logging.FileHandler(
        "logs/app.log",
        encoding="utf-8"
    )

    # Format log messages
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)