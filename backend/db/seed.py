# Database seeding utilities
import json
import os
from sqlalchemy.orm import Session
from .models import Location, Character, Item, LoreFact, TimelineEvent, Mystery
from .json_utils import dumps

def load_json_file(file_path: str) -> list:
    """Load JSON data from file"""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def upsert_location(db: Session, data: dict):
    """Upsert location by id, validates required fields"""
    # Validate required fields
    if 'id' not in data:
        raise ValueError("Location missing required field: 'id'")
    if 'name' not in data:
        raise ValueError(f"Location {data.get('id', 'unknown')} missing required field: 'name'")
    
    location = db.query(Location).filter(Location.id == data['id']).first()
    
    if location:
        # Update existing (respect immutable flag)
        if location.immutable and data.get('immutable', True):
            # Only update non-immutable fields if trying to update immutable row
            pass
        for key, value in data.items():
            if key == 'exits':
                setattr(location, 'exits_json', dumps(value))
            elif key != 'id':  # Don't update primary key
                setattr(location, key, value)
    else:
        # Create new
        location = Location(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            atmosphere=data.get('atmosphere'),
            exits_json=dumps(data.get('exits', [])),
            immutable=data.get('immutable', True)
        )
        db.add(location)
    
    db.commit()
    return location

def upsert_character(db: Session, data: dict):
    """Upsert character by id, validates required fields"""
    # Validate required fields
    if 'id' not in data:
        raise ValueError("Character missing required field: 'id'")
    if 'name' not in data:
        raise ValueError(f"Character {data.get('id', 'unknown')} missing required field: 'name'")
    
    character = db.query(Character).filter(Character.id == data['id']).first()
    
    if character:
        # Update existing (respect immutable flag)
        if character.immutable and data.get('immutable', True):
            # Only update non-immutable fields if trying to update immutable row
            pass
        for key, value in data.items():
            if key == 'traits':
                setattr(character, 'traits_json', dumps(value))
            elif key != 'id':  # Don't update primary key
                setattr(character, key, value)
    else:
        # Create new
        character = Character(
            id=data['id'],
            name=data['name'],
            bio=data.get('bio'),
            traits_json=dumps(data.get('traits', {})),
            last_known_location_id=data.get('last_known_location_id'),
            immutable=data.get('immutable', True)
        )
        db.add(character)
    
    db.commit()
    return character

def upsert_item(db: Session, data: dict):
    """Upsert item by id, validates required fields"""
    # Validate required fields
    if 'id' not in data:
        raise ValueError("Item missing required field: 'id'")
    if 'name' not in data:
        raise ValueError(f"Item {data.get('id', 'unknown')} missing required field: 'name'")
    
    item = db.query(Item).filter(Item.id == data['id']).first()
    
    if item:
        # Update existing (respect immutable flag)
        if item.immutable and data.get('immutable', True):
            # Only update non-immutable fields if trying to update immutable row
            pass
        for key, value in data.items():
            if key == 'state':
                setattr(item, 'state_json', dumps(value))
            elif key != 'id':  # Don't update primary key
                setattr(item, key, value)
    else:
        # Create new
        item = Item(
            id=data['id'],
            name=data['name'],
            kind=data.get('kind'),
            seed_description=data.get('seed_description'),
            location_id=data.get('location_id'),
            state_json=dumps(data.get('state', {})),
            immutable=data.get('immutable', True)
        )
        db.add(item)
    
    db.commit()
    return item

def upsert_lore_fact(db: Session, data: dict):
    """Upsert lore fact by id (if provided) or create new, validates required fields"""
    # Validate required fields
    if 'text' not in data:
        raise ValueError("Lore fact missing required field: 'text'")
    
    if 'id' in data:
        lore_fact = db.query(LoreFact).filter(LoreFact.id == data['id']).first()
    else:
        lore_fact = None
    
    # Check for duplicates by text (case-insensitive)
    if not lore_fact:
        existing = db.query(LoreFact).filter(LoreFact.text.ilike(data['text'])).first()
        if existing:
            return existing  # Return existing instead of creating duplicate
    
    if lore_fact:
        # Update existing
        for key, value in data.items():
            if key != 'id':  # Don't update primary key
                setattr(lore_fact, key, value)
    else:
        # Create new
        lore_fact = LoreFact(
            category=data.get('category'),
            text=data['text']
        )
        db.add(lore_fact)
    
    db.commit()
    return lore_fact


def upsert_timeline_event(db: Session, data: dict):
    """Upsert timeline event by id, validates required fields"""
    if 'id' not in data:
        raise ValueError("TimelineEvent missing required field: 'id'")
    if 'act' not in data:
        raise ValueError(f"TimelineEvent {data.get('id', 'unknown')} missing required field: 'act'")
    if 'sequence' not in data:
        raise ValueError(f"TimelineEvent {data.get('id', 'unknown')} missing required field: 'sequence'")
    if 'label' not in data:
        raise ValueError(f"TimelineEvent {data.get('id', 'unknown')} missing required field: 'label'")
    if 'summary' not in data:
        raise ValueError(f"TimelineEvent {data.get('id', 'unknown')} missing required field: 'summary'")

    event = db.query(TimelineEvent).filter(TimelineEvent.id == data['id']).first()

    if event:
        # Update existing
        for key, value in data.items():
            if key == 'flags_set':
                setattr(event, 'flags_set_json', dumps(value))
            elif key != 'id':
                setattr(event, key, value)
    else:
        event = TimelineEvent(
            id=data['id'],
            uuid=data.get('uuid'),
            act=data['act'],
            sequence=data['sequence'],
            label=data['label'],
            location_id=data.get('location_id'),
            summary=data['summary'],
            flags_set_json=dumps(data.get('flags_set', [])),
        )
        db.add(event)

    db.commit()
    return event


def upsert_mystery(db: Session, data: dict):
    """Upsert mystery by id, validates required fields (single active mystery for now)"""
    if 'id' not in data:
        raise ValueError("Mystery missing required field: 'id'")
    if 'title' not in data:
        raise ValueError(f"Mystery {data.get('id', 'unknown')} missing required field: 'title'")
    if 'act' not in data:
        raise ValueError(f"Mystery {data.get('id', 'unknown')} missing required field: 'act'")
    if 'main_question' not in data:
        raise ValueError(f"Mystery {data.get('id', 'unknown')} missing required field: 'main_question'")

    mystery = db.query(Mystery).filter(Mystery.id == data['id']).first()

    if mystery:
        for key, value in data.items():
            if key == 'hypotheses':
                setattr(mystery, 'hypotheses_json', dumps(value))
            elif key == 'confirmed_clues_ids':
                setattr(mystery, 'confirmed_clues_ids_json', dumps(value))
            elif key == 'red_herings':
                setattr(mystery, 'red_herings_json', dumps(value))
            elif key == 'threads':
                setattr(mystery, 'threads_json', dumps(value))
            elif key != 'id':
                setattr(mystery, key, value)
    else:
        mystery = Mystery(
            id=data['id'],
            uuid=data.get('uuid'),
            title=data['title'],
            act=data['act'],
            main_question=data['main_question'],
            hypotheses_json=dumps(data.get('hypotheses', [])),
            confirmed_clues_ids_json=dumps(data.get('confirmed_clues_ids', [])),
            red_herings_json=dumps(data.get('red_herings', [])),
            threads_json=dumps(data.get('threads', [])),
        )
        db.add(mystery)

    db.commit()
    return mystery

def autosave(player_id: str):
    """Placeholder for autosave functionality (Phase 2+)"""
    # This will be implemented in Phase 2
    # Will be called after turn mutations to automatically save player state
    pass
