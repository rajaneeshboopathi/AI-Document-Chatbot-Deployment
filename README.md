# AI Document Chatbot

A document question-answering chatbot built with Python, FastAPI, RAG, ChromaDB, and Ollama.

Users can upload PDF, TXT, or DOCX files and ask questions about the uploaded document. The application retrieves relevant document chunks and uses them as context for the LLM response.

## Features

- Upload PDF, TXT, and DOCX files
- Extract text from uploaded documents
- Split documents into chunks
- Generate embeddings using Sentence Transformers
- Store and search embeddings with ChromaDB
- Rerank retrieved chunks using a CrossEncoder
- Generate answers using Ollama and `llama3.2:3b`
- Show source document and page information
- Keep documents isolated between chat sessions
- Detect duplicate uploads using SHA-256
- Replace documents safely within a chat
- Store chat history using SQLite
- Handle simple casual messages such as greetings and thanks
- Log application activity and errors
- ChatGPT-style web interface

## Tech Stack

| Part | Technology |
|---|---|
| Language | Python |
| Backend | FastAPI |
| Server | Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| PDF extraction | PyMuPDF |
| DOCX extraction | python-docx |
| Embeddings | Sentence Transformers |
| Embedding model | `all-MiniLM-L6-v2` |
| Vector database | ChromaDB |
| Reranker | CrossEncoder |
| Reranker model | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| LLM | Ollama `llama3.2:3b` |
| Chat history | SQLite |

## Project Structure

```text
AI-Document-Chatbot/
│
├── app/
│   ├── routes/
│   │   ├── documents.py
│   │   ├── chat.py
│   │   └── history.py
│   │
│   ├── services/
│   │   ├── document_loader.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── ingestion.py
│   │   ├── llm.py
│   │   ├── rag.py
│   │   ├── file_utils.py
│   │   ├── document_registry.py
│   │   ├── chat_history.py
│   │   ├── chat_session.py
│   │   ├── reranker.py
│   │   └── intent_classifier.py
│   │
│   └── utils/
│       └── logger.py
│
├── data/
│   ├── uploads/
│   ├── chroma/
│   ├── processed_files.json
│   └── chat_history.db
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── tests/
├── logs/
├── main.py
├── requirements.txt
└── README.md
```

## How the RAG Pipeline Works

### Document upload

```text
Upload file
    ↓
Validate file
    ↓
Calculate SHA-256 hash
    ↓
Check for duplicate
    ↓
Extract text
    ↓
Create chunks
    ↓
Generate embeddings
    ↓
Store in ChromaDB
```

### Question answering

```text
User question
    ↓
Intent check
    ↓
Document question
    ↓
Create query embedding
    ↓
Search ChromaDB
    ↓
Retrieve relevant chunks
    ↓
CrossEncoder reranking
    ↓
Build context
    ↓
Ollama LLM
    ↓
Answer + source information
```

Simple messages such as `Hello`, `Thanks`, or `Goodbye` are handled directly without running the RAG pipeline.

## Installation

### 1. Clone or download the project

Open a terminal in the project folder:

```powershell
cd AI-Document-Chatbot
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## Ollama Setup

This project uses Ollama for local LLM generation.

Install Ollama and make sure it is running.

Pull the model used by the project:

```powershell
ollama pull llama3.2:3b
```

Check that the model is available:

```powershell
ollama list
```

The application expects Ollama to be available at:

```text
http://localhost:11434
```

## Run the Backend

From the project root:

```powershell
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

## Run the Frontend

The frontend is inside the `frontend` folder.

Open:

```text
frontend/index.html
```

in a browser after starting the FastAPI server.

## Using the Application

### 1. Start a chat

Open the frontend. A chat session is created automatically.

### 2. Upload a document

Click **Upload Document** and select:

- PDF
- TXT
- DOCX

The document is processed and stored in the vector database.

### 3. Ask a question

For example:

```text
What is my CGPA?
```

The system retrieves the relevant part of the document and generates an answer.

### 4. Check the source

The response also includes the source document and page where the information was retrieved.

### 5. Start another chat

Click **+ New Chat**.

Each chat has its own `chat_id`, so documents from different chats are kept separate.

## API Endpoints

### `POST /new-chat`

Creates a new chat session.

Example response:

```json
{
    "chat_id": "generated-chat-id"
}
```

### `POST /upload`

Uploads and processes a document.

Form data:

```text
chat_id
file
```

Supported files:

```text
.pdf
.txt
.docx
```

Example response:

```json
{
    "message": "File uploaded and processed successfully",
    "filename": "resume.pdf",
    "chunks_created": 4,
    "duplicate": false,
    "chat_id": "..."
}
```

### `POST /chat`

Asks a question about the current chat's document.

Request:

```json
{
    "question": "What is my CGPA?",
    "chat_id": "..."
}
```

Example response:

```json
{
    "answer": "Your CGPA is 7.89.",
    "sources": [
        {
            "document": "resume.pdf",
            "page": 1,
            "file_hash": "...",
            "chat_id": "..."
        }
    ]
}
```

### `GET /history`

Returns stored chat history.

## Document Processing

### PDF

PDF text is extracted page by page using PyMuPDF. The page number is stored with each chunk.

### TXT

The text file is read directly.

### DOCX

Text is extracted from the document paragraphs.

The current DOCX implementation uses page 1 for source information because it does not calculate Word document page layouts.

## Chunking

The extracted text is divided into smaller chunks before embeddings are generated.

The current chunk size is approximately 700 characters.

## Embeddings

The project uses:

```text
all-MiniLM-L6-v2
```

Each document chunk and user question is converted into an embedding so that the system can search based on semantic similarity.

## Vector Search

ChromaDB stores the document chunks, embeddings, and metadata.

Each chunk contains metadata such as:

```text
document
page
file_hash
chat_id
```

The question is embedded and used to search for relevant chunks.

The initial retrieval uses the top 10 results.

## Reranking

The retrieved chunks are reranked using:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The reranker compares the question with each retrieved chunk and selects the most relevant results.

The final top 5 results are used as context for the LLM.

## Duplicate Documents

Each uploaded file is processed with SHA-256 hashing.

If the same file is uploaded again in the same chat, the hash is detected and the document is not processed again.

This avoids unnecessary extraction, embedding generation, and vector insertion.

## Chat Isolation

Every chat has a unique `chat_id`.

The `chat_id` is stored with the document vectors.

When a question is asked, ChromaDB searches only within the current chat's vectors.

This prevents one chat from retrieving another chat's document.

## Document Replacement

If a new document is uploaded to a chat that already contains a document, the new document is processed first.

If processing fails, the newly created data is rolled back and the existing document is kept.

If processing succeeds, the previous document vectors are removed and the new document becomes the active document for that chat.

## Chat History

Chat history is stored in:

```text
data/chat_history.db
```

The history stores the chat ID, question, answer, and timestamp.

The frontend also keeps the active chat session in browser session storage, allowing the current chat to survive a normal page refresh.

## Logging

Application logs are stored in:

```text
logs/app.log
```

The application logs events such as:

- Document uploads
- Duplicate detection
- Document processing
- Chat requests
- Intent classification
- Errors

## Error Handling

The backend validates:

- Chat ID
- Question
- File name
- File type

It also handles failures during:

- File saving
- Hash calculation
- Document extraction
- Embedding generation
- Vector storage
- LLM generation
- Chat history storage

Errors are logged for debugging.

## Testing

The application was tested through FastAPI Swagger and the web frontend.

The following areas were tested:

- PDF upload
- TXT upload
- DOCX upload
- Unsupported file types
- Document question answering
- Source document and page information
- Duplicate document detection
- Chat isolation
- Document replacement
- Failed document processing rollback
- Casual conversation
- Chat history
- New chat creation
- Browser refresh
- Sidebar chat switching

## Example

If the uploaded document contains:

```text
Bachelor of Electronics and Communication Engineering
7.89 CGPA
```

The user can ask:

```text
What is my CGPA?
```

The system retrieves the relevant chunk and sends it to the local LLM.

Example response:

```text
Your CGPA is 7.89.
```

Source:

```text
Document: resume.pdf
Page: 1
```

## Limitations

- The LLM runs locally through Ollama and requires sufficient system resources.
- Scanned or image-only PDFs are not processed with OCR.
- DOCX page numbers are currently represented as page 1.
- The application does not currently include user authentication.
- The project is intended for local development and demonstration.

## Future Improvements

- OCR for scanned PDFs
- Multi-document conversations
- User authentication
- Streaming LLM responses
- Better table and image extraction
- Cloud deployment
- Automated unit and integration tests
- Docker deployment

## Author

AI Document Chatbot project built using Python, FastAPI, RAG, Sentence Transformers, ChromaDB, CrossEncoder, Ollama, SQLite, and JavaScript.
