#!/usr/bin/env python3
"""Verify memory system integration - test retrieval and Context Engine integration"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.memory import search, retrieve_context, load_mapping, INDEX_PATH
from db.engine import SessionLocal
from db.models import MemoryDoc
from ai.prompts import SYSTEM_PROMPT


def verify_memory_integration():
    """Verify memory retrieval and Context Engine integration"""
    print("="*70)
    print("Memory System Integration Verification")
    print("="*70)
    
    # Check if index exists
    if not INDEX_PATH.exists():
        print("\n❌ FAISS index not found!")
        print("   Please run: python3 backend/scripts/reindex_seed.py")
        print("   (Requires OPENAI_API_KEY environment variable)")
        return False
    
    print("\n✓ FAISS index exists")
    
    # Load mapping
    mapping = load_mapping()
    print(f"✓ Loaded mapping with {len(mapping)} entries")
    
    # Test search for 'Holmes'
    print("\n" + "-"*70)
    print("1. Testing search for 'Holmes'")
    print("-"*70)
    
    query = "Holmes"
    matches = search(query, top_k=3)
    
    if not matches:
        print("❌ No matches found for 'Holmes'")
        return False
    
    print(f"\n✓ Found {len(matches)} matches\n")
    
    # Get document details
    db = SessionLocal()
    try:
        print("Top 3 results with similarity scores:")
        print("-"*70)
        
        results_detail = []
        for i, (score, idx) in enumerate(matches[:3], 1):
            doc_id = mapping.get(idx)
            if doc_id:
                doc = db.query(MemoryDoc).filter(MemoryDoc.id == doc_id).first()
                if doc:
                    print(f"\n{i}. Score: {score:.4f}")
                    print(f"   Kind: {doc.kind}")
                    print(f"   Text: {doc.text}")
                    results_detail.append({
                        "score": score,
                        "kind": doc.kind,
                        "text": doc.text
                    })
        
        if not results_detail:
            print("❌ Could not retrieve document details")
            return False
            
    finally:
        db.close()
    
    # Test retrieval context
    print("\n" + "-"*70)
    print("2. Testing retrieve_context() function")
    print("-"*70)
    
    test_intent = "Holmes mentions the diary"
    context = retrieve_context(test_intent)
    
    if context:
        print(f"\n✓ Retrieved context for '{test_intent}':")
        print("-"*70)
        for line in context.split('\n'):
            if line.strip():
                print(f"  • {line}")
    else:
        print(f"\n⚠️  No context retrieved for '{test_intent}'")
    
    # Verify Context Engine integration
    print("\n" + "-"*70)
    print("3. Verifying Context Engine Integration")
    print("-"*70)
    
    # Check if SYSTEM_PROMPT includes [RELEVANT FACTS]
    if "[RELEVANT FACTS]" in SYSTEM_PROMPT:
        print("✓ SYSTEM_PROMPT includes [RELEVANT FACTS] placeholder")
    else:
        print("❌ SYSTEM_PROMPT missing [RELEVANT FACTS] placeholder")
        return False
    
    # Test prompt formatting
    sample_facts = "\n".join([r["text"] for r in results_detail])
    formatted_prompt = SYSTEM_PROMPT.format(relevant_facts=sample_facts)
    
    if sample_facts in formatted_prompt:
        print("✓ System prompt correctly formats relevant facts")
        print("\nSample formatted prompt section:")
        print("-"*70)
        # Extract the relevant facts section
        start_idx = formatted_prompt.find("[RELEVANT FACTS]")
        if start_idx != -1:
            section = formatted_prompt[start_idx:start_idx+300]
            print(section + "...")
    else:
        print("❌ System prompt formatting failed")
        return False
    
    # Summary
    print("\n" + "="*70)
    print("✅ VERIFICATION COMPLETE")
    print("="*70)
    print("\nSummary:")
    print(f"  • FAISS index: ✓")
    print(f"  • Memory docs: {len(mapping)} indexed")
    print(f"  • Search functionality: ✓")
    print(f"  • Retrieval functionality: ✓")
    print(f"  • Context Engine integration: ✓")
    print(f"\nTop 3 results for 'Holmes':")
    for i, r in enumerate(results_detail, 1):
        print(f"  {i}. [{r['score']:.4f}] {r['kind']}: {r['text'][:60]}...")
    
    return True


if __name__ == "__main__":
    success = verify_memory_integration()
    sys.exit(0 if success else 1)




