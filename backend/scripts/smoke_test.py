# Smoke test script - verify database is accessible and queryable
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.engine import SessionLocal
from db.models import (
    Location, Character, Item, LoreFact, Player, 
    Inventory, SeenFlag, TranscriptEvent, SaveSlot, EphemeralEvent
)

def smoke_test():
    """Run smoke tests on all database tables"""
    db = SessionLocal()
    
    try:
        print("Running smoke tests on database...\n")
        
        # Test 1: Locations
        locations = db.query(Location).all()
        print(f"✓ Locations: {len(locations)} records")
        if locations:
            print(f"  - Example: {locations[0].name} (id: {locations[0].id})")
        
        # Test 2: Characters
        characters = db.query(Character).all()
        print(f"✓ Characters: {len(characters)} records")
        if characters:
            print(f"  - Example: {characters[0].name} (id: {characters[0].id})")
        
        # Test 3: Items
        items = db.query(Item).all()
        print(f"✓ Items: {len(items)} records")
        if items:
            print(f"  - Example: {items[0].name} (id: {items[0].id}, kind: {items[0].kind})")
        
        # Test 4: Lore Facts
        lore_facts = db.query(LoreFact).all()
        print(f"✓ Lore Facts: {len(lore_facts)} records")
        if lore_facts:
            print(f"  - Example: {lore_facts[0].category} - {lore_facts[0].text[:50]}...")
        
        # Test 5: Players
        players = db.query(Player).all()
        print(f"✓ Players: {len(players)} records")
        
        # Test 6: Inventory
        inventory = db.query(Inventory).all()
        print(f"✓ Inventory: {len(inventory)} records")
        
        # Test 7: Seen Flags
        seen_flags = db.query(SeenFlag).all()
        print(f"✓ Seen Flags: {len(seen_flags)} records")
        
        # Test 8: Transcript Events
        transcript_events = db.query(TranscriptEvent).all()
        print(f"✓ Transcript Events: {len(transcript_events)} records")
        
        # Test 9: Save Slots
        save_slots = db.query(SaveSlot).all()
        print(f"✓ Save Slots: {len(save_slots)} records")
        
        # Test 10: Ephemeral Events
        ephemeral_events = db.query(EphemeralEvent).all()
        print(f"✓ Ephemeral Events: {len(ephemeral_events)} records")
        
        print("\n" + "="*50)
        print("SMOKE TEST PASSED: All tables are accessible")
        print(f"Total records across all tables: {len(locations) + len(characters) + len(items) + len(lore_facts) + len(players) + len(inventory) + len(seen_flags) + len(transcript_events) + len(save_slots) + len(ephemeral_events)}")
        return True
        
    except Exception as e:
        print(f"\n✗ SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = smoke_test()
    sys.exit(0 if success else 1)


