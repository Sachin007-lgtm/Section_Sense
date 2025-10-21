"""Utility: create database tables on the configured DATABASE_URL (Supabase/Postgres)

This script imports the application's SQLAlchemy metadata and runs
an idempotent create_all(). Use this when you want to ensure the
required tables (including contact_messages) exist in your Supabase DB.

Usage (PowerShell):
    # Ensure Backend/.env has a correct DATABASE_URL or set env var
    $env:DATABASE_URL = "postgresql://..."
    python .\Backend\create_supabase_tables.py

Note: The same create_all() is executed on FastAPI startup, but running
this script is useful to create tables proactively from your machine or
via CI prior to deploying the app.
"""
import os
import sys
from dotenv import load_dotenv

# Ensure we can import the package
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT_DIR))
sys.path.insert(0, PROJECT_ROOT)

load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, '.env'))

from app import database


def main():
    print("Using DATABASE_URL:", database.DATABASE_URL)

    # Quick connection test
    if not database.test_connection():
        print("ERROR: Could not connect to the database. Check DATABASE_URL and network access.")
        return 1

    # Initialize DB (imports models and runs create_all)
    try:
        database.init_db()
        print("Tables created/verified successfully.")
        return 0
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        return 2


if __name__ == '__main__':
    sys.exit(main())
