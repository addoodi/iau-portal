"""
CSV to PostgreSQL Migration Script
Migrates all data from CSV files to PostgreSQL database
"""
import os
import sys
import pandas as pd
from uuid import UUID
from datetime import datetime
import json

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, init_db, UserModel, EmployeeModel, UnitModel, LeaveRequestModel, AttendanceLogModel, EmailSettingsModel

# CSV file paths
DATA_DIR = "backend/data"
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
EMPLOYEES_CSV = os.path.join(DATA_DIR, "employees.csv")
UNITS_CSV = os.path.join(DATA_DIR, "units.csv")
LEAVE_REQUESTS_CSV = os.path.join(DATA_DIR, "leave_requests.csv")
ATTENDANCE_CSV = os.path.join(DATA_DIR, "attendance_logs.csv")
EMAIL_SETTINGS_CSV = os.path.join(DATA_DIR, "email_settings.csv")


def migrate_users(db):
    """Migrate users.csv to users table"""
    if not os.path.exists(USERS_CSV):
        print(f"[SKIP] {USERS_CSV} not found")
        return 0

    print(f"\n[MIGRATING] Users from {USERS_CSV}...")
    df = pd.read_csv(USERS_CSV, dtype={'id': str})

    # Filter out empty rows
    df = df[df['email'].notna()]

    count = 0
    for _, row in df.iterrows():
        user = UserModel(
            id=UUID(row['id']),
            email=row['email'],
            password_hash=row['password_hash'],
            role=row['role'],
            is_active=bool(row['is_active'])
        )
        db.add(user)
        count += 1

    print(f"[SUCCESS] Migrated {count} users")
    return count


def migrate_units(db):
    """Migrate units.csv to units table"""
    if not os.path.exists(UNITS_CSV):
        print(f"[SKIP] {UNITS_CSV} not found")
        return 0

    print(f"\n[MIGRATING] Units from {UNITS_CSV}...")
    df = pd.read_csv(UNITS_CSV)

    # Filter out empty rows
    df = df[df['name_en'].notna()]

    count = 0
    for _, row in df.iterrows():
        unit = UnitModel(
            id=int(row['id']),
            name_en=row['name_en'],
            name_ar=row['name_ar']
        )
        db.add(unit)
        count += 1

    print(f"[SUCCESS] Migrated {count} units")
    return count


def migrate_employees(db):
    """Migrate employees.csv to employees table"""
    if not os.path.exists(EMPLOYEES_CSV):
        print(f"[SKIP] {EMPLOYEES_CSV} not found")
        return 0

    print(f"\n[MIGRATING] Employees from {EMPLOYEES_CSV}...")
    df = pd.read_csv(EMPLOYEES_CSV, dtype={'id': str, 'manager_id': str, 'unit_id': str})

    # Filter out empty rows
    df = df[df['user_id'].notna()]

    count = 0
    for _, row in df.iterrows():
        # Handle optional fields
        manager_id = row.get('manager_id')
        if pd.isna(manager_id) or manager_id == '':
            manager_id = None
        else:
            manager_id = str(manager_id)

        signature_path = row.get('signature_path')
        if pd.isna(signature_path):
            signature_path = None

        employee = EmployeeModel(
            id=str(row['id']),
            user_id=UUID(row['user_id']),
            first_name_ar=row['first_name_ar'],
            last_name_ar=row['last_name_ar'],
            first_name_en=row['first_name_en'],
            last_name_en=row['last_name_en'],
            position_ar=row['position_ar'],
            position_en=row['position_en'],
            unit_id=int(row['unit_id']),
            manager_id=manager_id,
            start_date=row['start_date'],
            monthly_vacation_earned=float(row.get('monthly_vacation_earned', 2.5)),
            signature_path=signature_path,
            contract_auto_renewed=bool(row.get('contract_auto_renewed', False))
        )
        db.add(employee)
        count += 1

    print(f"[SUCCESS] Migrated {count} employees")
    return count


def migrate_leave_requests(db):
    """Migrate leave_requests.csv to leave_requests table"""
    if not os.path.exists(LEAVE_REQUESTS_CSV):
        print(f"[SKIP] {LEAVE_REQUESTS_CSV} not found")
        return 0

    print(f"\n[MIGRATING] Leave Requests from {LEAVE_REQUESTS_CSV}...")
    df = pd.read_csv(LEAVE_REQUESTS_CSV, dtype={'employee_id': str})

    # Filter out empty rows
    df = df[df['employee_id'].notna()]

    count = 0
    for _, row in df.iterrows():
        # Handle optional fields
        rejection_reason = row.get('rejection_reason')
        if pd.isna(rejection_reason):
            rejection_reason = None

        approval_date = row.get('approval_date')
        if pd.isna(approval_date):
            approval_date = None

        # Handle attachments (stored as JSON string in CSV)
        attachments = row.get('attachments', '[]')
        if pd.isna(attachments) or attachments == '':
            attachments = []
        elif isinstance(attachments, str):
            try:
                attachments = json.loads(attachments)
            except:
                attachments = eval(attachments) if attachments != '[]' else []

        leave_request = LeaveRequestModel(
            id=int(row['id']),
            employee_id=str(row['employee_id']),
            vacation_type=row['vacation_type'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            duration=int(row['duration']),
            status=row.get('status', 'Pending'),
            rejection_reason=rejection_reason,
            approval_date=approval_date,
            balance_used=int(row['balance_used']),
            attachments=attachments
        )
        db.add(leave_request)
        count += 1

    print(f"[SUCCESS] Migrated {count} leave requests")
    return count


def migrate_attendance(db):
    """Migrate attendance_logs.csv to attendance_logs table"""
    if not os.path.exists(ATTENDANCE_CSV):
        print(f"[SKIP] {ATTENDANCE_CSV} not found")
        return 0

    print(f"\n[MIGRATING] Attendance Logs from {ATTENDANCE_CSV}...")
    df = pd.read_csv(ATTENDANCE_CSV, dtype={'id': str, 'employee_id': str})

    # Filter out empty rows
    df = df[df['employee_id'].notna()]

    count = 0
    for _, row in df.iterrows():
        # Parse timestamps
        check_in = pd.to_datetime(row['check_in'])

        check_out = row.get('check_out')
        if pd.isna(check_out):
            check_out = None
        else:
            check_out = pd.to_datetime(check_out)

        attendance = AttendanceLogModel(
            id=UUID(row['id']),
            employee_id=str(row['employee_id']),
            date=row['date'],
            check_in=check_in,
            check_out=check_out,
            status=row.get('status', 'Present')
        )
        db.add(attendance)
        count += 1

    print(f"[SUCCESS] Migrated {count} attendance logs")
    return count


def migrate_email_settings(db):
    """Migrate email_settings.csv to email_settings table"""
    if not os.path.exists(EMAIL_SETTINGS_CSV):
        print(f"[SKIP] {EMAIL_SETTINGS_CSV} not found")
        return 0

    print(f"\n[MIGRATING] Email Settings from {EMAIL_SETTINGS_CSV}...")
    df = pd.read_csv(EMAIL_SETTINGS_CSV)

    # Filter out empty rows
    df = df[df['smtp_host'].notna()]

    count = 0
    for _, row in df.iterrows():
        settings = EmailSettingsModel(
            id=1,  # Only one record
            smtp_host=row['smtp_host'],
            smtp_port=int(row['smtp_port']),
            smtp_username=row['smtp_username'],
            smtp_password_hash=row['smtp_password_hash'],
            sender_email=row['sender_email'],
            is_active=bool(row.get('is_active', False))
        )
        db.add(settings)
        count += 1

    print(f"[SUCCESS] Migrated {count} email settings")
    return count


def main():
    """Main migration function"""
    print("="*60)
    print("CSV to PostgreSQL Migration Script")
    print("="*60)

    # Initialize database (create tables if they don't exist)
    print("\n[INIT] Initializing database tables...")
    init_db()

    # Create database session
    db = SessionLocal()

    try:
        # Migration order matters due to foreign key constraints
        # 1. Users (no dependencies)
        # 2. Units (no dependencies)
        # 3. Employees (depends on Users and Units)
        # 4. Leave Requests (depends on Employees)
        # 5. Attendance Logs (depends on Employees)
        # 6. Email Settings (no dependencies)

        total_migrated = 0

        total_migrated += migrate_users(db)
        db.commit()  # Commit after each table

        total_migrated += migrate_units(db)
        db.commit()

        total_migrated += migrate_employees(db)
        db.commit()

        total_migrated += migrate_leave_requests(db)
        db.commit()

        total_migrated += migrate_attendance(db)
        db.commit()

        total_migrated += migrate_email_settings(db)
        db.commit()

        print("\n" + "="*60)
        print(f"[SUCCESS] Migration completed!")
        print(f"Total records migrated: {total_migrated}")
        print("="*60)

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
