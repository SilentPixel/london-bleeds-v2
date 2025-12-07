# SQLAlchemy models
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from .engine import Base
from .json_utils import dumps, loads
from datetime import datetime

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    atmosphere = Column(Text)
    exits_json = Column(Text)  # JSON string
    immutable = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Location(id='{self.id}', name='{self.name}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "atmosphere": self.atmosphere,
            "exits": loads(self.exits_json) if self.exits_json else [],
            "immutable": self.immutable
        }

class Character(Base):
    __tablename__ = "characters"
    __table_args__ = (
        Index('idx_character_location', 'last_known_location_id'),
    )
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    bio = Column(Text)
    traits_json = Column(Text)  # JSON string
    last_known_location_id = Column(String, ForeignKey("locations.id"), nullable=True)
    immutable = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Character(id='{self.id}', name='{self.name}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
            "traits": loads(self.traits_json),
            "last_known_location_id": self.last_known_location_id,
            "immutable": self.immutable
        }

class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        Index('idx_item_location', 'location_id'),
        Index('idx_item_kind', 'kind'),
    )
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    kind = Column(String)  # item|clue|evidence
    seed_description = Column(Text)
    location_id = Column(String, ForeignKey("locations.id"), nullable=True)
    state_json = Column(Text)  # JSON string
    immutable = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Item(id='{self.id}', name='{self.name}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "seed_description": self.seed_description,
            "location_id": self.location_id,
            "state": loads(self.state_json),
            "immutable": self.immutable
        }

class LoreFact(Base):
    __tablename__ = "lore_facts"
    __table_args__ = (
        Index('idx_lore_category', 'category'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String)  # era|person|place|rule
    text = Column(Text, nullable=False)
    
    def __repr__(self):
        return f"<LoreFact(id={self.id}, category='{self.category}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "text": self.text
        }


class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    __table_args__ = (
        Index('idx_timeline_act', 'act'),
        Index('idx_timeline_sequence', 'sequence'),
    )

    id = Column(String, primary_key=True)
    uuid = Column(String, nullable=True)
    act = Column(String, nullable=False)
    sequence = Column(Integer, nullable=False)
    label = Column(String, nullable=False)
    location_id = Column(String, ForeignKey("locations.id"), nullable=True)
    summary = Column(Text, nullable=False)
    flags_set_json = Column(Text)  # JSON list of flags

    def __repr__(self):
        return f"<TimelineEvent(id='{self.id}', act='{self.act}', sequence={self.sequence})>"

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "act": self.act,
            "sequence": self.sequence,
            "label": self.label,
            "location_id": self.location_id,
            "summary": self.summary,
            "flags_set": loads(self.flags_set_json) if self.flags_set_json else [],
        }


class Mystery(Base):
    __tablename__ = "mysteries"
    __table_args__ = (
        Index('idx_mystery_act', 'act'),
    )

    id = Column(String, primary_key=True)
    uuid = Column(String, nullable=True)
    title = Column(String, nullable=False)
    act = Column(String, nullable=False)
    main_question = Column(Text, nullable=False)
    hypotheses_json = Column(Text)  # JSON list of strings
    confirmed_clues_ids_json = Column(Text)  # JSON list of item ids
    red_herings_json = Column(Text)  # JSON list of strings
    threads_json = Column(Text)  # JSON list of {label, description}

    def __repr__(self):
        return f"<Mystery(id='{self.id}', title='{self.title}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "title": self.title,
            "act": self.act,
            "main_question": self.main_question,
            "hypotheses": loads(self.hypotheses_json) if self.hypotheses_json else [],
            "confirmed_clues_ids": loads(self.confirmed_clues_ids_json) if self.confirmed_clues_ids_json else [],
            "red_herings": loads(self.red_herings_json) if self.red_herings_json else [],
            "threads": loads(self.threads_json) if self.threads_json else [],
        }

class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        Index('idx_player_location', 'current_location_id'),
        Index('idx_player_created', 'created_at'),
    )
    
    id = Column(String, primary_key=True)  # uuid
    profile_name = Column(String, nullable=False)
    current_location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    vars_json = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Player(id='{self.id}', profile_name='{self.profile_name}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "profile_name": self.profile_name,
            "current_location_id": self.current_location_id,
            "vars": loads(self.vars_json),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        Index('idx_inventory_player', 'player_id'),
        Index('idx_inventory_item', 'item_id'),
    )
    
    player_id = Column(String, ForeignKey("players.id"), primary_key=True)
    item_id = Column(String, ForeignKey("items.id"), primary_key=True)
    quantity = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<Inventory(player_id='{self.player_id}', item_id='{self.item_id}', quantity={self.quantity})>"
    
    def to_dict(self):
        return {
            "player_id": self.player_id,
            "item_id": self.item_id,
            "quantity": self.quantity
        }

class SeenFlag(Base):
    __tablename__ = "seen_flags"
    __table_args__ = (
        Index('idx_seen_player', 'player_id'),
        Index('idx_seen_entity', 'entity_kind', 'entity_id'),
    )
    
    player_id = Column(String, primary_key=True)
    entity_kind = Column(String, primary_key=True)  # location|character|item|lore
    entity_id = Column(String, primary_key=True)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SeenFlag(player_id='{self.player_id}', entity_kind='{self.entity_kind}', entity_id='{self.entity_id}')>"
    
    def to_dict(self):
        return {
            "player_id": self.player_id,
            "entity_kind": self.entity_kind,
            "entity_id": self.entity_id,
            "first_seen_at": self.first_seen_at.isoformat() if self.first_seen_at else None
        }

class TranscriptEvent(Base):
    __tablename__ = "transcript_events"
    __table_args__ = (
        Index('idx_transcript_player', 'player_id'),
        Index('idx_transcript_player_turn', 'player_id', 'turn'),
        Index('idx_transcript_created', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String, nullable=False)
    turn = Column(Integer)
    kind = Column(String)  # command|narration|state_change|error
    payload_json = Column(Text)  # JSON string
    markdown = Column(Text)  # Markdown narration text
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TranscriptEvent(id={self.id}, player_id='{self.player_id}', kind='{self.kind}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "turn": self.turn,
            "kind": self.kind,
            "payload": loads(self.payload_json),
            "markdown": self.markdown,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class SaveSlot(Base):
    __tablename__ = "save_slots"
    __table_args__ = (
        Index('idx_save_player', 'player_id'),
        Index('idx_save_created', 'created_at'),
    )
    
    id = Column(String, primary_key=True)  # uuid
    player_id = Column(String, ForeignKey("players.id"), nullable=False)
    name = Column(String, nullable=False)
    snapshot_json = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SaveSlot(id='{self.id}', player_id='{self.player_id}', name='{self.name}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "name": self.name,
            "snapshot": loads(self.snapshot_json),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class EphemeralEvent(Base):
    __tablename__ = "ephemeral_events"
    __table_args__ = (
        Index('idx_ephemeral_player', 'player_id'),
        Index('idx_ephemeral_location', 'location_id'),
        Index('idx_ephemeral_created', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String, nullable=False)
    location_id = Column(String)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<EphemeralEvent(id={self.id}, player_id='{self.player_id}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "location_id": self.location_id,
            "text": self.text,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class MemoryDoc(Base):
    __tablename__ = "memory_docs"
    __table_args__ = (
        Index('idx_memory_kind', 'kind'),
        Index('idx_memory_stale', 'stale'),
        Index('idx_memory_entity', 'entity_id'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kind = Column(String)  # seed_lore | lore_rule | known_fact | entity_card | transcript
    entity_id = Column(String, nullable=True)
    text = Column(Text)
    importance = Column(Integer, default=0)
    stale = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MemoryDoc(id={self.id}, kind='{self.kind}', stale={self.stale})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "entity_id": self.entity_id,
            "text": self.text,
            "importance": self.importance,
            "stale": self.stale,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
