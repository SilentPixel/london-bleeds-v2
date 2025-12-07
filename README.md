# London Bleeds - Victorian Mystery Game Backend

A FastAPI backend for a Victorian-era mystery game set in 1888 London.

## Setup

### Prerequisites
- Python 3.11+
- pip or uv

### Installation

1. Install dependencies:
```bash
pip install -e .
```

### Database Setup

#### Initial Setup
```bash
# Initialize database schema
python scripts/init_db.py

# Or use Alembic migrations (recommended)
python -m alembic upgrade head

# Seed initial data
python scripts/seed_db.py
```

#### Alembic Migrations
```bash
# Create a new migration
python -m alembic revision --autogenerate -m "description"

# Apply migrations
python -m alembic upgrade head

# Revert last migration
python -m alembic downgrade -1

# Show current revision
python -m alembic current
```

#### Seeding the DB
```bash
python scripts/init_db.py
python scripts/seed_db.py
```

#### Run dev server
```bash
uvicorn app.main:app --reload
```

Then verify:
- `GET http://127.0.0.1:8000/health` → `{ "status": "ok" }`
- `GET http://127.0.0.1:8000/debug/locations` → seeded locations appear.

#### Run integrity and smoke tests
```bash
python scripts/check_integrity.py && python scripts/smoke_test.py
```

#### Clean rebuild (optional)
Rebuild everything from scratch:
```bash
python scripts/rebuild_all.py
```

This script will:
1. Delete existing `game.db`
2. Recreate all tables
3. Seed the database
4. Run integrity checks
5. Run smoke tests
6. Exit with error code if any step fails

## Project Structure

```
/backend
  /app          # FastAPI application
  /db           # Database models and engine
  /api          # API routes
  /scripts      # Database scripts
  /seed         # Seed data files
```

## API Endpoints

### Health
- `GET /health` - Health check

### Debug (Development)
- `GET /debug/locations` - List all locations
- `GET /debug/characters` - List all characters  
- `GET /debug/items` - List all items

## Database Models

The database includes tables for:
- **locations** - Game world locations
- **characters** - NPCs and characters
- **items** - Objects, clues, and evidence
- **lore_facts** - Immutable world knowledge
- **players** - Player state and progress
- **inventory** - Player item ownership
- **seen_flags** - Player discovery tracking
- **transcript_events** - Game history
- **save_slots** - Game saves
- **ephemeral_events** - Temporary AI-generated content

## Docker

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t london-bleeds .

# Run the container
docker run -p 8000:8000 -v $(pwd)/backend/data:/app/data london-bleeds
```

The application will be available at `http://localhost:8000`

## Development

### Pre-commit Hooks

Install pre-commit hooks for code quality:
```bash
pip install pre-commit
pre-commit install
```

Hooks include:
- **black** - Code formatter
- **ruff** - Fast Python linter
- **mypy** - Static type checker

### Tech Stack

The project uses:
- FastAPI for the web framework
- SQLAlchemy for database ORM
- SQLite for the database
- Pydantic for data validation
- orjson for fast JSON serialization
- Alembic for database migrations
