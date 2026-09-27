from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.documents import router as document_router
from app.routes.chat import router as chat_router
from app.routes.history import router as history_router


app = FastAPI()


# Allow the frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(document_router)
app.include_router(chat_router)
app.include_router(history_router)


@app.get("/")
def home():
    return {
        "message": "AI Document Chatbot is running!"
    }