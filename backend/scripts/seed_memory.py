#!/usr/bin/env python3
"""Seed memory_docs table from existing lore_facts"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.engine import SessionLocal
from db.models import LoreFact, MemoryDoc
from ai.memory import promote_fact


def seed_memory_from_lore():
    """Create MemoryDoc entries from existing LoreFact entries"""
    db = SessionLocal()
    try:
        # Get all lore facts
        lore_facts = db.query(LoreFact).all()
        
        if not lore_facts:
            print("No lore facts found. Run seed_db.py first.")
            return
        
        # Check if memory docs already exist
        existing_count = db.query(MemoryDoc).filter(MemoryDoc.kind == "seed_lore").count()
        if existing_count > 0:
            print(f"Memory docs already seeded ({existing_count} existing). Skipping.")
            return
        
        # Create memory docs from lore facts
        count = 0
        for lore in lore_facts:
            # Determine kind based on category
            kind_map = {
                "era": "seed_lore",
                "person": "seed_lore",
                "place": "seed_lore",
                "rule": "lore_rule"
            }
            kind = kind_map.get(lore.category, "seed_lore")
            
            doc = MemoryDoc(
                kind=kind,
                text=lore.text,
                importance=1 if lore.category == "rule" else 0,
                stale=False
            )
            db.add(doc)
            count += 1
        
        db.commit()
        print(f"✅ Created {count} memory docs from lore facts.")
        print(f"   Run 'python scripts/reindex_seed.py' to build the FAISS index.")
    except Exception as e:
        print(f"Error seeding memory: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_memory_from_lore()

