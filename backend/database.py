"""
SQLAlchemy Database Models and Configuration
Maps to Pydantic models in models.py
"""
import os
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, TypeDecorator
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import uuid
from datetime import datetime


# Database-agnostic UUID type
# Uses native PostgreSQL UUID when available, falls back to String(36) for SQLite
class GUID(TypeDecorator):
    """Platform-independent UUID type. Uses PostgreSQL UUID, otherwise String(36)."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
        return value


# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://iau_admin:iau_secure_password_2024@localhost:5432/iau_portal"
)

# Detect if using SQLite (for testing)
_is_sqlite = DATABASE_URL.startswith("sqlite")

# Create SQLAlchemy engine with appropriate settings
_engine_kwargs = {
    "echo": False,
}

if not _is_sqlite:
    _engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })
else:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# ==============================================
# Database Models (SQLAlchemy ORM)
# ==============================================

class UserModel(Base):
    """User authentication and authorization"""
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'admin', 'manager', 'employee', 'dean'
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship to employee
    employee = relationship("EmployeeModel", back_populates="user", uselist=False)


class EmployeeModel(Base):
    """Employee information and HR data"""
    __tablename__ = "employees"

    id = Column(String(50), primary_key=True)  # "IAU-001" or "0000001"
    user_id = Column(GUID, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    first_name_ar = Column(String(100), nullable=False)
    last_name_ar = Column(String(100), nullable=False)
    first_name_en = Column(String(100), nullable=False)
    last_name_en = Column(String(100), nullable=False)
    position_ar = Column(String(200), nullable=False)
    position_en = Column(String(200), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False, index=True)
    manager_id = Column(String(50), ForeignKey("employees.id"), nullable=True, index=True)
    start_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    monthly_vacation_earned = Column(Float, default=2.5, nullable=False)
    signature_path = Column(String(500), nullable=True)
    contract_auto_renewed = Column(Boolean, default=False, nullable=False)
    employee_type = Column(String(20), default='contractor', nullable=False)  # 'permanent' or 'contractor'

    # Relationships
    user = relationship("UserModel", back_populates="employee")
    unit = relationship("UnitModel", back_populates="employees")
    manager = relationship("EmployeeModel", remote_side=[id], backref="subordinates")
    leave_requests = relationship("LeaveRequestModel", back_populates="employee")
    attendance_logs = relationship("AttendanceLogModel", back_populates="employee")


class UnitModel(Base):
    """Organizational units/departments"""
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_en = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)

    # Relationships
    employees = relationship("EmployeeModel", back_populates="unit")


class LeaveRequestModel(Base):
    """Vacation/leave requests"""
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.id"), nullable=False, index=True)
    vacation_type = Column(String(50), nullable=False)  # 'Annual', 'Sick', etc.
    start_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    end_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    duration = Column(Integer, nullable=False)
    status = Column(String(20), default='Pending', nullable=False)  # 'Pending', 'Approved', 'Rejected'
    rejection_reason = Column(Text, nullable=True)
    approval_date = Column(String(10), nullable=True)  # YYYY-MM-DD
    balance_used = Column(Integer, nullable=False)
    attachments = Column(JSON, default=list, nullable=False)  # List of file paths

    # Relationships
    employee = relationship("EmployeeModel", back_populates="leave_requests")


class AttendanceLogModel(Base):
    """Employee attendance tracking"""
    __tablename__ = "attendance_logs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(50), ForeignKey("employees.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=True)
    status = Column(String(20), default='Present', nullable=False)  # 'Present', 'Absent', 'Late'

    # Relationships
    employee = relationship("EmployeeModel", back_populates="attendance_logs")


class EmailSettingsModel(Base):
    """SMTP email configuration (singleton)"""
    __tablename__ = "email_settings"

    id = Column(Integer, primary_key=True, default=1)  # Only one record
    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False)
    smtp_username = Column(String(255), nullable=False)
    smtp_password_hash = Column(String(255), nullable=False)
    sender_email = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)


class PortalSettingsModel(Base):
    """Global portal settings (singleton)"""
    __tablename__ = "portal_settings"

    id = Column(Integer, primary_key=True, default=1)  # Only one record
    max_carry_over_days = Column(Integer, default=15, nullable=False)


class AuditLogModel(Base):
    """
    Audit log for tracking critical user actions.

    Security and compliance feature that records:
    - Who performed an action (user_id, email)
    - What action was performed (create, approve, reject, update, delete)
    - When it occurred (timestamp)
    - What entity was affected (entity_type, entity_id)
    - Additional context (details JSON)
    - Request metadata (IP address, user agent)

    Use cases:
    - Compliance audits (who approved which leave requests)
    - Security investigations (unauthorized access attempts)
    - Debugging (trace user actions leading to issues)
    - Analytics (user activity patterns)
    """
    __tablename__ = "audit_logs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    user_id = Column(GUID, nullable=True)  # None for system actions
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False, index=True)  # e.g., "leave_request_approved"
    entity_type = Column(String(50), nullable=False, index=True)  # e.g., "leave_request"
    entity_id = Column(String(100), nullable=False, index=True)  # ID of affected entity
    details = Column(Text, nullable=True)  # JSON string with additional context
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)


# ==============================================
# Database Helper Functions
# ==============================================

def get_db():
    """
    Dependency for FastAPI endpoints
    Creates a database session and closes it after use

    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(UserModel).all()
            return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _run_migrations(db):
    """
    Run schema migrations for existing databases.
    Adds missing columns that were added after initial deployment.
    """
    from sqlalchemy import text, inspect

    inspector = inspect(engine)

    # Check if employees table exists
    if 'employees' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('employees')]

        # Migration: Add employee_type column if missing
        if 'employee_type' not in columns:
            print("[MIGRATION] Adding employee_type column to employees table...")
            db.execute(text(
                "ALTER TABLE employees ADD COLUMN employee_type VARCHAR(20) DEFAULT 'contractor' NOT NULL"
            ))
            db.commit()
            print("[MIGRATION] employee_type column added successfully")


def init_db():
    """
    Initialize database tables
    Run this once to create all tables
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Run migrations for existing databases
    db = SessionLocal()
    try:
        _run_migrations(db)
    except Exception as e:
        print(f"[MIGRATION] Migration error (may be expected on fresh install): {e}")
        db.rollback()
    finally:
        db.close()

    # Create default unit for admin if it doesn't exist
    db = SessionLocal()
    try:
        existing_unit = db.query(UnitModel).filter(UnitModel.id == 1).first()
        if not existing_unit:
            default_unit = UnitModel(
                name_en="Administration",
                name_ar="الإدارة"
            )
            db.add(default_unit)
            db.commit()
            db.refresh(default_unit)
            print(f"[SEED] Created default Administration unit (ID: {default_unit.id})")
    except Exception as e:
        print(f"[SEED] Default unit already exists or error: {e}")
        db.rollback()

    # Create default portal settings if they don't exist
    try:
        existing_settings = db.query(PortalSettingsModel).filter(PortalSettingsModel.id == 1).first()
        if not existing_settings:
            default_settings = PortalSettingsModel(max_carry_over_days=15)
            db.add(default_settings)
            db.commit()
            print("[SEED] Created default portal settings (max_carry_over_days=15)")
    except Exception as e:
        print(f"[SEED] Portal settings already exist or error: {e}")
        db.rollback()

    db.close()

    print("[SUCCESS] Database tables created successfully!")


def drop_all_tables():
    """
    WARNING: Drop all tables (use carefully!)
    """
    print("WARNING: Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("[SUCCESS] All tables dropped")


if __name__ == "__main__":
    # If run directly, create all tables
    print(f"Database URL: {DATABASE_URL}")
    init_db()
