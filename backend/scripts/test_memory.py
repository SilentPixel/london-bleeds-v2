#!/usr/bin/env python3
"""Test the memory system - search and retrieval"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.memory import search, retrieve_context, load_mapping
from db.engine import SessionLocal
from db.models import MemoryDoc


def test_memory():
    """Test memory search and retrieval"""
    print("Testing Memory System\n" + "="*50)
    
    # Check if index exists
    from ai.memory import INDEX_PATH
    if not INDEX_PATH.exists():
        print("❌ FAISS index not found. Run 'python scripts/reindex_seed.py' first.")
        return False
    
    # Check mapping
    mapping = load_mapping()
    print(f"✓ Loaded mapping with {len(mapping)} entries")
    
    # Check memory docs
    db = SessionLocal()
    try:
        doc_count = db.query(MemoryDoc).filter(MemoryDoc.stale == False).count()
        print(f"✓ Found {doc_count} non-stale memory documents")
        
        if doc_count == 0:
            print("⚠️  No memory documents found. Run 'python scripts/seed_memory.py' first.")
            return False
    finally:
        db.close()
    
    # Test search
    print("\n" + "-"*50)
    print("Testing search functionality:")
    test_queries = ["Holmes", "diary", "Whitechapel", "murder"]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        matches = search(query, top_k=3)
        if matches:
            print(f"  Found {len(matches)} matches:")
            for score, idx in matches:
                print(f"    - Score: {score:.3f}, Index: {idx}")
        else:
            print("  No matches found")
    
    # Test retrieval
    print("\n" + "-"*50)
    print("Testing retrieval context:")
    test_intent = "Holmes mentions the diary"
    context = retrieve_context(test_intent)
    if context:
        print(f"Query: '{test_intent}'")
        print(f"Retrieved context ({len(context)} chars):")
        print(f"  {context[:200]}..." if len(context) > 200 else f"  {context}")
    else:
        print("No context retrieved")
    
    print("\n" + "="*50)
    print("✅ Memory system test completed!")
    return True


if __name__ == "__main__":
    success = test_memory()
    sys.exit(0 if success else 1)

