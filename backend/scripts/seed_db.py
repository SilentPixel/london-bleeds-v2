# Database seeding script
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.engine import SessionLocal
from db.seed import (
    load_json_file,
    upsert_location,
    upsert_character,
    upsert_item,
    upsert_lore_fact,
    upsert_timeline_event,
    upsert_mystery,
)

def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        seed_dir = os.path.join(script_dir, '..', 'seed')
        
        # Seed locations
        locations_data = load_json_file(os.path.join(seed_dir, 'locations.json'))
        for data in locations_data:
            upsert_location(db, data)
        
        # Seed characters
        characters_data = load_json_file(os.path.join(seed_dir, 'characters.json'))
        for data in characters_data:
            upsert_character(db, data)
        
        # Seed items
        items_data = load_json_file(os.path.join(seed_dir, 'items.json'))
        for data in items_data:
            upsert_item(db, data)
        
        # Seed lore facts
        lore_data = load_json_file(os.path.join(seed_dir, 'lore.json'))
        for data in lore_data:
            upsert_lore_fact(db, data)

        # Seed timeline events
        timeline_data = load_json_file(os.path.join(seed_dir, 'timeline.json'))
        for data in timeline_data:
            upsert_timeline_event(db, data)

        # Seed mystery (single object file)
        mystery_path = os.path.join(seed_dir, 'mystery.json')
        mystery_data = load_json_file(mystery_path)
        # Support either a dict or a single-element list
        if isinstance(mystery_data, dict):
            upsert_mystery(db, mystery_data)
        elif isinstance(mystery_data, list) and mystery_data:
            upsert_mystery(db, mystery_data[0])
        
        # Print counts per table
        from db.models import Location, Character, Item, LoreFact, TimelineEvent, Mystery
        location_count = db.query(Location).count()
        character_count = db.query(Character).count()
        item_count = db.query(Item).count()
        lore_count = db.query(LoreFact).count()
        timeline_count = db.query(TimelineEvent).count()
        mystery_count = db.query(Mystery).count()
        
        print("Database seeding completed successfully!")
        print(f"Counts per table:")
        print(f"  locations: {location_count}")
        print(f"  characters: {character_count}")
        print(f"  items: {item_count}")
        print(f"  lore_facts: {lore_count}")
        print(f"  timeline_events: {timeline_count}")
        print(f"  mysteries: {mystery_count}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
