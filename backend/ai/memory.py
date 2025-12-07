# Memory module - FAISS vector storage and retrieval
import faiss
import numpy as np
from openai import OpenAI
from pathlib import Path
from typing import List, Tuple, Dict
from sqlalchemy.orm import Session
import json
import os
from dotenv import load_dotenv

from db.engine import SessionLocal
from db.models import MemoryDoc

# Load environment variables from .env file
# Load from project root (two levels up from backend/ai/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

EMBED_MODEL = "text-embedding-3-large"
INDEX_PATH = Path(__file__).parent.parent.parent / "data" / "faiss.index"
MAPPING_PATH = Path(__file__).parent.parent.parent / "data" / "faiss_mapping.json"

# Ensure data directory exists
INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_openai_client() -> OpenAI:
    """Get OpenAI client instance"""
    # OpenAI() automatically reads from OPENAI_API_KEY environment variable
    # which is loaded via load_dotenv() above
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
    return OpenAI(api_key=api_key)


def embed(texts: List[str]) -> np.ndarray:
    """Embed texts using OpenAI embeddings API"""
    client = get_openai_client()
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vectors = np.array([d.embedding for d in response.data]).astype("float32")
    faiss.normalize_L2(vectors)
    return vectors


def build_index(vectors: np.ndarray, doc_ids: List[int]) -> faiss.IndexFlatIP:
    """Build FAISS index from vectors and save to disk"""
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    if INDEX_PATH.exists():
        INDEX_PATH.unlink()  # Remove old index
    faiss.write_index(index, str(INDEX_PATH))
    
    # Save mapping from FAISS index position to MemoryDoc ID
    mapping = {str(i): doc_id for i, doc_id in enumerate(doc_ids)}
    with open(MAPPING_PATH, 'w') as f:
        json.dump(mapping, f)
    
    return index


def search(query: str, top_k: int = 3) -> List[Tuple[float, int]]:
    """Search FAISS index for similar documents"""
    if not INDEX_PATH.exists():
        return []
    
    index = faiss.read_index(str(INDEX_PATH))
    q_vec = embed([query])
    D, I = index.search(q_vec, top_k)
    
    # Filter out invalid indices (-1 means no match)
    results = [(float(d), int(i)) for d, i in zip(D[0], I[0]) if i >= 0]
    return results


def load_mapping() -> Dict[int, int]:
    """Load FAISS index to MemoryDoc ID mapping"""
    if not MAPPING_PATH.exists():
        return {}
    with open(MAPPING_PATH, 'r') as f:
        return {int(k): int(v) for k, v in json.load(f).items()}


def retrieve_context(player_intent: str) -> str:
    """Retrieve relevant facts from memory based on player intent"""
    db = SessionLocal()
    try:
        matches = search(player_intent, top_k=3)
        if not matches:
            return ""
        
        # Map FAISS indices to MemoryDoc IDs
        mapping = load_mapping()
        doc_ids = [mapping.get(idx) for _, idx in matches if idx in mapping]
        
        # Fetch documents by ID
        docs = db.query(MemoryDoc).filter(
            MemoryDoc.id.in_(doc_ids),
            MemoryDoc.stale == False
        ).all()
        
        # Create a lookup dict for quick access
        doc_dict = {doc.id: doc.text for doc in docs}
        
        # Return facts in order of match relevance
        facts = []
        for _, idx in matches:
            doc_id = mapping.get(idx)
            if doc_id and doc_id in doc_dict:
                facts.append(doc_dict[doc_id])
        
        return "\n".join(facts)
    finally:
        db.close()


def promote_fact(text: str, kind: str = "known_fact", entity_id: str = None, importance: int = 0):
    """Store a new known fact in memory"""
    db = SessionLocal()
    try:
        doc = MemoryDoc(
            kind=kind,
            text=text,
            entity_id=entity_id,
            importance=importance,
            stale=False
        )
        db.add(doc)
        db.commit()
        return doc
    finally:
        db.close()


def mark_stale(doc_id: int):
    """Mark a memory document as stale"""
    db = SessionLocal()
    try:
        doc = db.query(MemoryDoc).filter(MemoryDoc.id == doc_id).first()
        if doc:
            doc.stale = True
            db.commit()
    finally:
        db.close()


# Minimal test harness
if __name__ == "__main__":
    q = "Holmes mentions the diary"
    print(f"Searching for: '{q}'")
    results = search(q)
    print(f"Results: {results}")
    
    # Show detailed results if index exists
    if results:
        mapping = load_mapping()
        db = SessionLocal()
        try:
            print("\nTop matches:")
            for score, idx in results[:3]:
                doc_id = mapping.get(idx)
                if doc_id:
                    doc = db.query(MemoryDoc).filter(MemoryDoc.id == doc_id).first()
                    if doc:
                        print(f"  Score: {score:.3f} | {doc.kind} | {doc.text[:80]}...")
        finally:
            db.close()
    else:
        print("No results found. Make sure the FAISS index is built (run scripts/reindex_seed.py)")

