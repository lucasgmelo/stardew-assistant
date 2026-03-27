"""
FastAPI server — expõe o pipeline RAG via SSE.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_ollama import OllamaEmbeddings, OllamaLLM

from config import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL, LLM_MODEL
from chat import retrieve, format_context, build_prompt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Conectando ao ChromaDB...")
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_collection(COLLECTION_NAME)
print(f"Coleção carregada: {_collection.count()} chunks")

print(f"Carregando modelos Ollama ({EMBED_MODEL}, {LLM_MODEL})...")
_embeddings = OllamaEmbeddings(model=EMBED_MODEL)
_llm = OllamaLLM(model=LLM_MODEL, temperature=0.3)
print("Pronto.")


class HistoryMessage(BaseModel):
    role: str  # "user" | "assistant"
    text: str

class ChatRequest(BaseModel):
    question: str
    game_state: str = ""
    history: list[HistoryMessage] = []


@app.get("/health")
def health():
    return {"status": "ok", "chunks": _collection.count()}


@app.post("/chat")
def chat(req: ChatRequest):
    def generate():
        chunks = retrieve(_collection, _embeddings, req.question)
        context = format_context(chunks)
        history = [{"role": m.role, "text": m.text} for m in req.history]
        prompt = build_prompt(context, req.question, req.game_state, history)

        sources = list({c["meta"]["title"] for c in chunks})
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

        for token in _llm.stream(prompt):
            yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
