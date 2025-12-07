# Database integrity check script
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.engine import SessionLocal
from db.models import Location, Character, Item, LoreFact
from db.json_utils import loads

def check_integrity():
    """Check database integrity"""
    db = SessionLocal()
    errors = []
    
    try:
        # Check 1: All exits_json.to locations exist
        locations = db.query(Location).all()
        location_ids = {loc.id for loc in locations}
        
        for loc in locations:
            if loc.exits_json:
                exits = loads(loc.exits_json) if loc.exits_json else []
                for exit in exits:
                    if isinstance(exit, dict) and 'to' in exit:
                        if exit['to'] not in location_ids:
                            errors.append(f"Location '{loc.id}' has exit to non-existent location '{exit['to']}'")
        
        print("✓ Check 1: All exits point to valid locations")
        
        # Check 2: No orphan characters.last_known_location_id
        characters = db.query(Character).all()
        orphan_chars = []
        
        for char in characters:
            if char.last_known_location_id and char.last_known_location_id not in location_ids:
                orphan_chars.append(char.id)
                errors.append(f"Character '{char.id}' references non-existent location '{char.last_known_location_id}'")
        
        if not orphan_chars:
            print("✓ Check 2: No orphan character location references")
        else:
            print(f"✗ Check 2: Found {len(orphan_chars)} orphan character references")
        
        # Check 3: Items referencing valid location_id
        items = db.query(Item).all()
        invalid_items = []
        
        for item in items:
            if item.location_id and item.location_id not in location_ids:
                invalid_items.append(item.id)
                errors.append(f"Item '{item.id}' references non-existent location '{item.location_id}'")
        
        if not invalid_items:
            print("✓ Check 3: All item location references are valid")
        else:
            print(f"✗ Check 3: Found {len(invalid_items)} items with invalid location references")
        
        # Check 4: Lore facts are non-empty and unique
        lore_facts = db.query(LoreFact).all()
        empty_lore = []
        seen_texts = {}
        
        for lore in lore_facts:
            # Check non-empty
            if not lore.text or not lore.text.strip():
                empty_lore.append(lore.id)
                errors.append(f"Lore fact {lore.id} has empty text")
            
            # Check uniqueness
            text_key = lore.text.strip().lower()
            if text_key in seen_texts:
                errors.append(f"Lore fact {lore.id} duplicates lore fact {seen_texts[text_key]} (text: '{lore.text[:50]}...')")
            else:
                seen_texts[text_key] = lore.id
        
        if not empty_lore:
            print("✓ Check 4: All lore facts are non-empty")
        else:
            print(f"✗ Check 4: Found {len(empty_lore)} empty lore facts")
        
        if len(seen_texts) == len(lore_facts):
            print("✓ Check 4: All lore facts are unique")
        else:
            print(f"✗ Check 4: Found {len(lore_facts) - len(seen_texts)} duplicate lore facts")
        
        # Summary
        print("\n" + "="*50)
        if errors:
            print(f"INTEGRITY CHECK FAILED: {len(errors)} error(s) found\n")
            for error in errors:
                print(f"  ✗ {error}")
            return False
        else:
            print("INTEGRITY CHECK PASSED: Database is consistent")
            return True
            
    except Exception as e:
        print(f"Error during integrity check: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = check_integrity()
    sys.exit(0 if success else 1)


