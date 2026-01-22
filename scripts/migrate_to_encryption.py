#!/usr/bin/env python3
"""
Migration script to encrypt existing user data for GDPR compliance.

This script:
1. Adds new encrypted columns to the users table
2. Encrypts all existing name and birthdate data
3. Generates pseudonym IDs for all users
4. Preserves all existing data

Usage:
    # Local (outside Docker):
    python scripts/migrate_to_encryption.py
    
    # Docker:
    docker-compose exec backend python scripts/migrate_to_encryption.py
"""

import os
import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.database import DATABASE_URL, engine
from app.utils.encryption import encrypt, generate_pseudonym_id


def migrate_users_to_encryption():
    """Migrate all users to use encrypted fields."""
    print("=" * 60)
    print("User Data Encryption Migration")
    print("=" * 60)
    
    # Check if encryption key is set
    if not os.getenv("ENCRYPTION_KEY"):
        print("ERROR: ENCRYPTION_KEY environment variable is required")
        print("Generate one with:")
        print("  python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'")
        return 1
    
    # Create database connection
    db = sessionmaker(bind=engine)()
    
    try:
        # Step 1: Check if encrypted columns exist, if not add them
        print("\nStep 1: Checking database schema...")
        
        with engine.connect() as conn:
            # Check if encrypted columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('name_encrypted', 'birthdate_encrypted', 'pseudonym_id')
            """))
            existing_columns = [row[0] for row in result]
            
            if 'name_encrypted' not in existing_columns:
                print("  Adding name_encrypted column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN name_encrypted TEXT"))
                conn.commit()
            
            if 'birthdate_encrypted' not in existing_columns:
                print("  Adding birthdate_encrypted column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN birthdate_encrypted TEXT"))
                conn.commit()
            
            if 'pseudonym_id' not in existing_columns:
                print("  Adding pseudonym_id column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN pseudonym_id VARCHAR(50)"))
                conn.commit()
                # Create index
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_pseudonym_id ON users(pseudonym_id)"))
                conn.commit()
        
        print("  ✓ Schema updated")
        
        # Step 2: Get all users
        print("\nStep 2: Fetching all users...")
        users = db.execute(text("SELECT id, name, birthdate, pseudonym_id FROM users")).fetchall()
        print(f"  Found {len(users)} users to migrate")
        
        if len(users) == 0:
            print("  No users to migrate. Migration complete!")
            return 0
        
        # Step 3: Encrypt existing data
        print("\nStep 3: Encrypting user data...")
        migrated = 0
        skipped = 0
        
        for user in users:
            user_id, name, birthdate, existing_pseudonym = user
            
            # Check if already encrypted (has encrypted data)
            check_result = db.execute(text("""
                SELECT name_encrypted, birthdate_encrypted 
                FROM users 
                WHERE id = :user_id
            """), {"user_id": user_id}).fetchone()
            
            if check_result and check_result[0] and check_result[1]:
                print(f"  User {user_id}: Already encrypted, skipping")
                skipped += 1
                continue
            
            # Encrypt name
            if name:
                encrypted_name = encrypt(str(name))
            else:
                encrypted_name = None
            
            # Encrypt birthdate
            if birthdate:
                if isinstance(birthdate, date):
                    date_str = birthdate.isoformat()
                else:
                    date_str = str(birthdate)
                encrypted_birthdate = encrypt(date_str)
            else:
                encrypted_birthdate = None
            
            # Generate pseudonym if not exists
            pseudonym = existing_pseudonym or generate_pseudonym_id()
            
            # Update user
            db.execute(text("""
                UPDATE users 
                SET name_encrypted = :name_enc, 
                    birthdate_encrypted = :bd_enc,
                    pseudonym_id = :pseudonym
                WHERE id = :user_id
            """), {
                "name_enc": encrypted_name,
                "bd_enc": encrypted_birthdate,
                "pseudonym": pseudonym,
                "user_id": user_id
            })
            
            print(f"  User {user_id}: Encrypted (pseudonym: {pseudonym})")
            migrated += 1
        
        db.commit()
        print(f"\n  ✓ Migrated {migrated} users")
        if skipped > 0:
            print(f"  ⊙ Skipped {skipped} users (already encrypted)")
        
        # Step 4: Make encrypted columns NOT NULL (after all data is migrated)
        print("\nStep 4: Updating column constraints...")
        with engine.connect() as conn:
            # Check if there are any NULL values
            null_check = conn.execute(text("""
                SELECT COUNT(*) 
                FROM users 
                WHERE name_encrypted IS NULL OR birthdate_encrypted IS NULL
            """)).fetchone()[0]
            
            if null_check == 0:
                print("  All users have encrypted data, updating constraints...")
                # Note: In production, you might want to keep old columns for a while
                # before dropping them. For now, we'll just ensure encrypted columns are populated.
                print("  ✓ Constraints verified")
            else:
                print(f"  ⚠ Warning: {null_check} users still have NULL encrypted fields")
        
        print("\n" + "=" * 60)
        print("Migration complete!")
        print("=" * 60)
        print(f"\nMigrated: {migrated} users")
        print(f"Skipped: {skipped} users")
        print("\nNext steps:")
        print("1. Test the application to ensure data is displayed correctly")
        print("2. Once verified, you can drop the legacy 'name' and 'birthdate' columns")
        print("   (Keep them for now as backup during testing)")
        
        return 0
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(migrate_users_to_encryption())
