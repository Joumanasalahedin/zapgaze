#!/usr/bin/env python3
"""
Fix user table columns to make legacy columns nullable.

This script makes the legacy 'name' and 'birthdate' columns nullable
so that new users can be created with only encrypted data.

Usage:
    docker-compose exec backend python scripts/fix_user_columns.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.database import engine


def fix_user_columns():
    """Make legacy columns nullable."""
    print("=" * 60)
    print("Fixing User Table Columns")
    print("=" * 60)

    try:
        with engine.connect() as conn:
            # Check current constraints
            print("\nStep 1: Checking current column constraints...")
            result = conn.execute(
                text("""
                SELECT column_name, is_nullable, data_type
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name IN ('name', 'birthdate', 'name_encrypted', 'birthdate_encrypted')
                ORDER BY column_name
            """)
            )

            columns = {row[0]: {"nullable": row[1], "type": row[2]} for row in result}

            for col_name, info in columns.items():
                status = "NULLABLE" if info["nullable"] == "YES" else "NOT NULL"
                print(f"  {col_name}: {info['type']} ({status})")

            # Make legacy columns nullable
            print("\nStep 2: Making legacy columns nullable...")

            if "name" in columns and columns["name"]["nullable"] == "NO":
                print("  Making 'name' column nullable...")
                conn.execute(text("ALTER TABLE users ALTER COLUMN name DROP NOT NULL"))
                conn.commit()
                print("  ✓ 'name' column is now nullable")

            if "birthdate" in columns and columns["birthdate"]["nullable"] == "NO":
                print("  Making 'birthdate' column nullable...")
                conn.execute(
                    text("ALTER TABLE users ALTER COLUMN birthdate DROP NOT NULL")
                )
                conn.commit()
                print("  ✓ 'birthdate' column is now nullable")

            # Verify changes
            print("\nStep 3: Verifying changes...")
            result = conn.execute(
                text("""
                SELECT column_name, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name IN ('name', 'birthdate')
            """)
            )

            for row in result:
                status = "NULLABLE" if row[1] == "YES" else "NOT NULL"
                print(f"  {row[0]}: {status}")

        print("\n" + "=" * 60)
        print("✓ Columns fixed successfully!")
        print("=" * 60)
        print("\nYou can now create new users with encrypted data only.")
        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(fix_user_columns())
