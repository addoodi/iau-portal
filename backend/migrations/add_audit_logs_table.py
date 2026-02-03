"""
Database Migration: Add Audit Logs Table

Creates the audit_logs table for tracking critical user actions.

Run this migration after deploying the security fixes to add
audit logging capability to the database.

Usage:
    python backend/migrations/add_audit_logs_table.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import engine, Base, SessionLocal, AuditLogModel
from sqlalchemy import inspect


def check_table_exists(table_name: str) -> bool:
    """Check if a table already exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def upgrade():
    """
    Create audit_logs table.

    Safe to run multiple times - checks if table exists first.
    """
    print("=" * 60)
    print("IAU Portal - Audit Logs Table Migration")
    print("=" * 60)
    print()

    # Check if table already exists
    if check_table_exists("audit_logs"):
        print("[OK] Table 'audit_logs' already exists - skipping creation")
        print()
        return

    print("Creating 'audit_logs' table...")

    try:
        # Create only the audit_logs table
        AuditLogModel.__table__.create(engine, checkfirst=True)
        print("[OK] Successfully created 'audit_logs' table")
        print()

        # Verify table was created
        if check_table_exists("audit_logs"):
            print("[OK] Verification successful - table exists in database")

            # Show table structure
            inspector = inspect(engine)
            columns = inspector.get_columns("audit_logs")

            print()
            print("Table Structure:")
            print("-" * 60)
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"  {col['name']:20} {str(col['type']):30} {nullable}")
            print("-" * 60)

            # Show indexes
            indexes = inspector.get_indexes("audit_logs")
            if indexes:
                print()
                print("Indexes:")
                print("-" * 60)
                for idx in indexes:
                    cols = ", ".join(idx['column_names'])
                    print(f"  {idx['name']}: ({cols})")
                print("-" * 60)
        else:
            print("[ERROR] Verification failed - table not found after creation")
            return

    except Exception as e:
        print(f"[ERROR] Error creating table: {str(e)}")
        print()
        raise

    print()
    print("=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart the backend server")
    print("2. Test audit logging by logging in")
    print("3. View logs via: GET /api/admin/audit-logs")
    print()


def downgrade():
    """
    Drop audit_logs table.

    WARNING: This will delete all audit log data!
    """
    print("=" * 60)
    print("IAU Portal - Rollback Audit Logs Table")
    print("=" * 60)
    print()

    if not check_table_exists("audit_logs"):
        print("[OK] Table 'audit_logs' does not exist - nothing to rollback")
        print()
        return

    print("[WARNING] This will permanently delete all audit log data!")
    confirm = input("Type 'yes' to confirm rollback: ")

    if confirm.lower() != 'yes':
        print("Rollback cancelled")
        return

    try:
        print("Dropping 'audit_logs' table...")
        AuditLogModel.__table__.drop(engine, checkfirst=True)
        print("[OK] Successfully dropped 'audit_logs' table")
    except Exception as e:
        print(f"[ERROR] Error dropping table: {str(e)}")
        raise

    print()
    print("Rollback completed")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        downgrade()
    else:
        upgrade()
