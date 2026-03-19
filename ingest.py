"""
Lê os arquivos de wiki_pages/, chunkeia e indexa no ChromaDB
usando embeddings do nomic-embed-text via Ollama.
"""

import os
import json
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from config import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL

WIKI_DIR = "./wiki_pages"
METADATA_FILE = "./wiki_pages/metadata.json"


def load_documents() -> list[dict]:
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError("metadata.json não encontrado. Rode scraper.py primeiro.")

    with open(METADATA_FILE) as f:
        metadata = json.load(f)

    docs = []
    for entry in metadata:
        filepath = os.path.join(WIKI_DIR, entry["file"])
        if not os.path.exists(filepath):
            print(f"  AVISO: arquivo não encontrado: {filepath}")
            continue
        with open(filepath, encoding="utf-8") as f:
            text = f.read()
        docs.append({
            "text": text,
            "title": entry["title"],
            "url": entry["url"],
            "path": entry["path"],
            "file": entry["file"],
        })

    print(f"Carregados {len(docs)} documentos")
    return docs


def chunk_documents(docs: list[dict]) -> tuple[list[str], list[dict], list[str]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n## ", "\n\n", "\n", ". ", " "],
    )

    texts, metadatas, ids = [], [], []
    for doc in docs:
        chunks = splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['file']}__chunk{i}"
            texts.append(chunk)
            metadatas.append({
                "title": doc["title"],
                "url": doc["url"],
                "path": doc["path"],
                "chunk_index": i,
            })
            ids.append(chunk_id)

    print(f"Total de chunks: {len(texts)}")
    return texts, metadatas, ids


def ingest():
    docs = load_documents()
    texts, metadatas, ids = chunk_documents(docs)

    print(f"Carregando modelo de embeddings: {EMBED_MODEL}")
    embeddings_model = OllamaEmbeddings(model=EMBED_MODEL)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Recria a coleção se já existir (re-ingest limpo)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Coleção existente removida, recriando...")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Processa em batches para não estourar memória/timeout
    batch_size = 50
    total = len(texts)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch_texts = texts[start:end]
        batch_meta = metadatas[start:end]
        batch_ids = ids[start:end]

        print(f"  Embedding batch {start}-{end} / {total}...")
        batch_embeddings = embeddings_model.embed_documents(batch_texts)

        collection.add(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_texts,
            metadatas=batch_meta,
        )

    print(f"\nIngest concluído. {total} chunks indexados em {CHROMA_PATH}/")


if __name__ == "__main__":
    ingest()
