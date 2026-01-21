#!/usr/bin/env python3
"""
Migration script to migrate data from SQLite to PostgreSQL.

Usage:
    python scripts/migrate_sqlite_to_postgres.py

This script will:
1. Connect to the SQLite database
2. Connect to PostgreSQL
3. Migrate all data preserving relationships
4. Verify data integrity
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_sqlite_connection(sqlite_path: str = "zapgaze.db"):
    """Connect to SQLite database."""
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")
    return sqlite3.connect(sqlite_path)


def get_postgres_connection(database_url: str = None):
    """Connect to PostgreSQL database."""
    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://zapgaze_user:changeme_in_production@localhost:5432/zapgaze"
        )
    return psycopg2.connect(database_url)


def migrate_table(sqlite_cursor, pg_cursor, table_name, columns, order_by=None):
    """Migrate a single table from SQLite to PostgreSQL."""
    print(f"Migrating table: {table_name}...")
    
    # Build SELECT query
    select_query = f"SELECT {', '.join(columns)} FROM {table_name}"
    if order_by:
        select_query += f" ORDER BY {order_by}"
    
    # Fetch all data
    sqlite_cursor.execute(select_query)
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"  No data to migrate for {table_name}")
        return 0
    
    # Build INSERT query with placeholders
    placeholders = ", ".join(["%s"] * len(columns))
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Insert data
    try:
        execute_values(pg_cursor, insert_query, rows)
        count = len(rows)
        print(f"  Migrated {count} rows")
        return count
    except Exception as e:
        print(f"  Error migrating {table_name}: {e}")
        raise


def reset_sequences(pg_cursor):
    """Reset PostgreSQL sequences to match max IDs."""
    print("Resetting sequences...")
    
    tables = [
        "users", "sessions", "intakes", "results", "task_events",
        "calibration_points", "session_features"
    ]
    
    for table in tables:
        try:
            pg_cursor.execute(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM {table}));")
        except Exception as e:
            print(f"  Could not reset sequence for {table}: {e}")


def verify_migration(sqlite_conn, pg_conn):
    """Verify that migration was successful by comparing row counts."""
    print("\nVerifying migration...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    tables = [
        "users", "sessions", "intakes", "results", "task_events",
        "calibration_points", "session_features"
    ]
    
    all_match = True
    for table in tables:
        try:
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = pg_cursor.fetchone()[0]
            
            status = "✓" if sqlite_count == pg_count else "✗"
            print(f"  {status} {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
            
            if sqlite_count != pg_count:
                all_match = False
        except Exception as e:
            print(f"  ✗ Error verifying {table}: {e}")
            all_match = False
    
    return all_match


def main():
    """Main migration function."""
    print("=" * 60)
    print("SQLite to PostgreSQL Migration Script")
    print("=" * 60)
    
    # Get database URLs
    sqlite_path = os.getenv("SQLITE_PATH", "zapgaze.db")
    postgres_url = os.getenv(
        "DATABASE_URL",
        "postgresql://zapgaze_user:changeme_in_production@localhost:5432/zapgaze"
    )
    
    print(f"\nSQLite source: {sqlite_path}")
    print(f"PostgreSQL target: {postgres_url.split('@')[1] if '@' in postgres_url else 'hidden'}")
    
    # Connect to databases
    try:
        print("\nConnecting to SQLite...")
        sqlite_conn = get_sqlite_connection(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        print("✓ Connected to SQLite")
        
        print("Connecting to PostgreSQL...")
        pg_conn = get_postgres_connection(postgres_url)
        pg_cursor = pg_conn.cursor()
        print("✓ Connected to PostgreSQL")
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return 1
    
    # Create tables in PostgreSQL if they don't exist
    print("\nCreating tables in PostgreSQL...")
    try:
        engine = create_engine(postgres_url)
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created/verified")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return 1
    
    # Disable foreign key checks temporarily (PostgreSQL doesn't need this, but good practice)
    pg_cursor.execute("SET session_replication_role = 'replica';")
    
    try:
        # Migrate tables in order (respecting foreign key dependencies)
        print("\nMigrating data...")
        
        # 1. Users (no dependencies)
        migrate_table(
            sqlite_cursor, pg_cursor,
            "users",
            ["id", "name", "birthdate"]
        )
        
        # 2. Sessions (depends on users)
        migrate_table(
            sqlite_cursor, pg_cursor,
            "sessions",
            ["id", "user_id", "session_uid", "started_at", "stopped_at", "status"],
            "id"
        )
        
        # 3. Intakes (depends on users, sessions)
        migrate_table(
            sqlite_cursor, pg_cursor,
            "intakes",
            ["id", "user_id", "session_uid", "answers_json", "total_score", "symptom_group", "created_at"],
            "id"
        )
        
        # 4. Calibration points (depends on sessions)
        migrate_table(
            sqlite_cursor, pg_cursor,
            "calibration_points",
            ["id", "session_id", "screen_x", "screen_y", "measured_x", "measured_y", "timestamp"],
            "id"
        )
        
        # 5. Task events (depends on sessions)
        migrate_table(
            sqlite_cursor, pg_cursor,
            "task_events",
            ["id", "session_id", "timestamp", "event_type", "stimulus", "response"],
            "id"
        )
        
        # 6. Results (depends on sessions)
        migrate_table(
            sqlite_cursor, pg_cursor,
            "results",
            ["id", "session_id", "data"],
            "id"
        )
        
        # 7. Session features (depends on sessions)
        migrate_table(
            sqlite_cursor, pg_cursor,
            "session_features",
            [
                "id", "session_id", "user_id",
                "mean_fixation_duration", "fixation_count", "gaze_dispersion",
                "saccade_count", "saccade_rate",
                "total_blinks", "blink_rate",
                "go_reaction_time_mean", "go_reaction_time_sd",
                "omission_errors", "commission_errors",
                "started_at", "stopped_at"
            ],
            "id"
        )
        
        # Re-enable foreign key checks
        pg_cursor.execute("SET session_replication_role = 'origin';")
        
        # Reset sequences
        reset_sequences(pg_cursor)
        
        # Commit transaction
        pg_conn.commit()
        print("\n✓ Migration completed successfully")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Verify migration
    if verify_migration(sqlite_conn, pg_conn):
        print("\n✓ Verification passed - all data migrated correctly")
    else:
        print("\n⚠ Verification failed - please check the data manually")
        return 1
    
    # Close connections
    sqlite_conn.close()
    pg_conn.close()
    
    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
