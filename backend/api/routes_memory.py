# Memory debug endpoints
from fastapi import APIRouter
from ai.memory import search, retrieve_context, load_mapping
from db.engine import SessionLocal
from db.models import MemoryDoc

router = APIRouter()


@router.get("/memory/search")
def memory_search(q: str):
    """Search memory index and return top-k matches"""
    matches = search(q, top_k=3)
    
    # Get document details for each match using mapping
    db = SessionLocal()
    try:
        mapping = load_mapping()
        doc_ids = [mapping.get(idx) for _, idx in matches if idx in mapping]
        
        if not doc_ids:
            return {
                "query": q,
                "matches": []
            }
        
        docs = db.query(MemoryDoc).filter(MemoryDoc.id.in_(doc_ids)).all()
        doc_dict = {doc.id: doc for doc in docs}
        
        results = []
        for score, idx in matches:
            doc_id = mapping.get(idx)
            if doc_id and doc_id in doc_dict:
                doc = doc_dict[doc_id]
                results.append({
                    "score": score,
                    "index": idx,
                    "id": doc.id,
                    "kind": doc.kind,
                    "text": doc.text,
                    "entity_id": doc.entity_id
                })
        
        return {
            "query": q,
            "matches": results
        }
    finally:
        db.close()


@router.get("/memory/retrieve")
def memory_retrieve(q: str):
    """Test retrieval context function"""
    context = retrieve_context(q)
    return {
        "query": q,
        "context": context
    }

