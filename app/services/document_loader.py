import os
import pymupdf
from docx import Document


def extract_text_from_pdf(file_path):

    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document):

        text = page.get_text()

        pages.append({
            "page": page_number + 1,
            "text": text
        })

    document.close()

    return pages


def extract_text_from_txt(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        text = file.read()

    return [
        {
            "page": 1,
            "text": text
        }
    ]


def extract_text_from_docx(file_path):

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    full_text = "\n".join(paragraphs)

    return [
        {
            "page": 1,
            "text": full_text
        }
    ]


def extract_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":

        return extract_text_from_pdf(file_path)

    elif extension == ".txt":

        return extract_text_from_txt(file_path)

    elif extension == ".docx":

        return extract_text_from_docx(file_path)

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )