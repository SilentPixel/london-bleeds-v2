#!/usr/bin/env python3
"""Rebuild FAISS index from all non-stale MemoryDoc entries"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.memory import embed, build_index
from db.engine import SessionLocal
from db.models import MemoryDoc
import numpy as np


def reindex():
    """Rebuild FAISS index from all non-stale memory documents"""
    db = SessionLocal()
    try:
        docs = db.query(MemoryDoc).filter(MemoryDoc.stale == False).order_by(MemoryDoc.id).all()
        if not docs:
            print("No memory docs to embed.")
            return
        
        texts = [d.text for d in docs]
        doc_ids = [d.id for d in docs]
        
        print(f"Embedding {len(texts)} memory documents...")
        
        vectors = embed(texts)
        build_index(vectors, doc_ids)
        
        print(f"✅ Indexed {len(texts)} memory docs.")
        print(f"   Vector dimension: {vectors.shape[1]}")
    finally:
        db.close()


if __name__ == "__main__":
    reindex()

