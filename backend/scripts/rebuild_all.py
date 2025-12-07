#!/usr/bin/env python3
"""
Clean rebuild script - deletes database, recreates tables, reseeds data, and runs tests
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Main rebuild process"""
    print("="*60)
    print("CLEAN REBUILD - London Bleeds Database")
    print("="*60)
    
    # Step 1: Delete game.db if present
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Deleted existing {db_path}")
    else:
        print("✓ No existing database file to delete")
    
    # Step 2: Recreate tables
    print("\n2. Recreating database tables...")
    try:
        from db.engine import Base, engine
        from db import models  # Import all models to register them
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return 1
    
    # Step 3: Reseed data
    print("\n3. Seeding database...")
    try:
        from scripts.seed_db import seed_database
        seed_database()
        print("✓ Database seeded successfully")
    except Exception as e:
        print(f"✗ Failed to seed database: {e}")
        return 1
    
    # Step 4: Run integrity tests
    print("\n4. Running integrity checks...")
    try:
        from scripts.check_integrity import check_integrity
        if not check_integrity():
            print("✗ Integrity checks failed")
            return 1
    except Exception as e:
        print(f"✗ Integrity checks failed: {e}")
        return 1
    
    # Step 5: Run smoke tests
    print("\n5. Running smoke tests...")
    try:
        from scripts.smoke_test import smoke_test
        if not smoke_test():
            print("✗ Smoke tests failed")
            return 1
    except Exception as e:
        print(f"✗ Smoke tests failed: {e}")
        return 1
    
    # Success
    print("\n" + "="*60)
    print("✓ CLEAN REBUILD COMPLETED SUCCESSFULLY")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())


