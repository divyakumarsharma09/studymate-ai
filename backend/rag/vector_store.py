import uuid

import chromadb

from backend.rag.embedder import embed_texts, embed_question

CHROMA_PATH = "data/chroma"

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name="documents",
    configuration={"hnsw": {"space": "cosine"}},
)


def add_document(filename: str, chunks: list) -> str:
    doc_id = uuid.uuid4().hex
    texts = [chunk["text"] for chunk in chunks]
    vectors = embed_texts(texts)
    _collection.add(
        ids=[f"{doc_id}-{i}" for i in range(len(chunks))],
        documents=texts,
        embeddings=vectors,
        metadatas=[
            {"doc_id": doc_id, "filename": filename, "page": chunk["page"]}
            for chunk in chunks
        ],
    )
    return doc_id


def search(question: str, doc_id: str, top_k: int = 4) -> list:
    query_vector = embed_question(question)
    results = _collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        where={"doc_id": doc_id},
    )
    hits = []
    for text, meta, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({"text": text, "page": meta["page"], "score": round(1 - distance, 3)})
    return hits