#!/usr/bin/env python
"""
Initialize database and create tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from app.models import *

def init_database():
    """Create all database tables"""
    print("Creating database tables...")

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")

    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
