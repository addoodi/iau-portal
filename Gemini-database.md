# IAU Portal: Database Schema Reference

**Last Updated:** 2026-01-04
**Database:** PostgreSQL 16 Alpine
**ORM:** SQLAlchemy 2.0+
**Migration Status:** ✅ Complete (CSV → PostgreSQL)

---

## 1. Overview

The IAU Portal uses **PostgreSQL** as its production database with **SQLAlchemy ORM** for data access. This document defines the complete database schema as implemented in `backend/database.py` and `backend/db_repositories.py`.

### Migration History
- **Before (Dec 2024 - Jan 2026)**: CSV files in `backend/data/`
- **After (Jan 2026)**: PostgreSQL with ACID transactions, foreign key constraints, and connection pooling

### Database Connection
```python
# backend/database.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://iau_admin:iau_secure_password_2024@localhost:5432/iau_portal"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
```

---

## 2. Database Schema

### 2.1. `users` Table
**Purpose:** Stores authentication credentials and user roles

**SQLAlchemy Model:**
```python
class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'admin', 'dean', 'manager', 'employee'
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship
    employee = relationship("EmployeeModel", back_populates="user", uselist=False)
```

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid.uuid4() | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Login email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `role` | VARCHAR(50) | NOT NULL | User role: admin, dean, manager, employee |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account active status |

**Indexes:**
- Primary key index on `id`
- Unique index on `email`

---

### 2.2. `employees` Table
**Purpose:** Stores employee profiles and HR information

**SQLAlchemy Model:**
```python
class EmployeeModel(Base):
    __tablename__ = "employees"

    id = Column(String(50), primary_key=True)  # "IAU-001" or "0000001"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)
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

    # Relationships
    user = relationship("UserModel", back_populates="employee")
    unit = relationship("UnitModel", back_populates="employees")
    manager = relationship("EmployeeModel", remote_side=[id], backref="subordinates")
    leave_requests = relationship("LeaveRequestModel", back_populates="employee")
    attendance_logs = relationship("AttendanceLogModel", back_populates="employee")
```

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | VARCHAR(50) | PRIMARY KEY | Employee ID (e.g., "IAU-001", "0000001") |
| `user_id` | UUID | FOREIGN KEY(users.id), UNIQUE, NOT NULL, INDEX | Links to users table |
| `first_name_ar` | VARCHAR(100) | NOT NULL | First name in Arabic |
| `last_name_ar` | VARCHAR(100) | NOT NULL | Last name in Arabic |
| `first_name_en` | VARCHAR(100) | NOT NULL | First name in English |
| `last_name_en` | VARCHAR(100) | NOT NULL | Last name in English |
| `position_ar` | VARCHAR(200) | NOT NULL | Job title in Arabic |
| `position_en` | VARCHAR(200) | NOT NULL | Job title in English |
| `unit_id` | INTEGER | FOREIGN KEY(units.id), NOT NULL, INDEX | Department/unit assignment |
| `manager_id` | VARCHAR(50) | FOREIGN KEY(employees.id), NULLABLE, INDEX | Direct manager (self-referencing FK) |
| `start_date` | VARCHAR(10) | NOT NULL | Contract start date (YYYY-MM-DD) |
| `monthly_vacation_earned` | FLOAT | NOT NULL, DEFAULT 2.5 | Monthly vacation accrual rate (days) |
| `signature_path` | VARCHAR(500) | NULLABLE | Path to signature image file |
| `contract_auto_renewed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Auto-renewal flag |

**Indexes:**
- Primary key index on `id`
- Unique index on `user_id`
- Index on `unit_id` (foreign key)
- Index on `manager_id` (foreign key)

**Foreign Keys:**
- `user_id` → `users.id` (One-to-one relationship)
- `unit_id` → `units.id` (Many-to-one relationship)
- `manager_id` → `employees.id` (Self-referencing, one-to-many)

---

### 2.3. `units` Table
**Purpose:** Organizational units/departments

**SQLAlchemy Model:**
```python
class UnitModel(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_en = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)

    # Relationships
    employees = relationship("EmployeeModel", back_populates="unit")
```

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique unit identifier |
| `name_en` | VARCHAR(200) | NOT NULL | Unit name in English |
| `name_ar` | VARCHAR(200) | NOT NULL | Unit name in Arabic |

**Indexes:**
- Primary key index on `id`

**Default Data:**
- Unit ID 1: "Administration" / "الإدارة" (created automatically by `init_db()`)

---

### 2.4. `leave_requests` Table
**Purpose:** Vacation/leave request records

**SQLAlchemy Model:**
```python
class LeaveRequestModel(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.id"), nullable=False, index=True)
    vacation_type = Column(String(50), nullable=False)  # 'Annual', 'Sick', 'Emergency', 'Exams'
    start_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    end_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    duration = Column(Integer, nullable=False)
    status = Column(String(20), default='Pending', nullable=False)  # 'Pending', 'Approved', 'Rejected', 'Cancelled'
    rejection_reason = Column(Text, nullable=True)
    approval_date = Column(String(10), nullable=True)  # YYYY-MM-DD
    balance_used = Column(Integer, nullable=False)
    attachments = Column(JSON, default=list, nullable=False)  # List of file paths

    # Relationships
    employee = relationship("EmployeeModel", back_populates="leave_requests")
```

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique request identifier |
| `employee_id` | VARCHAR(50) | FOREIGN KEY(employees.id), NOT NULL, INDEX | Employee making the request |
| `vacation_type` | VARCHAR(50) | NOT NULL | Type: Annual, Sick, Emergency, Exams |
| `start_date` | VARCHAR(10) | NOT NULL | Start date (YYYY-MM-DD) |
| `end_date` | VARCHAR(10) | NOT NULL | End date (YYYY-MM-DD) |
| `duration` | INTEGER | NOT NULL | Number of days requested |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'Pending' | Status: Pending, Approved, Rejected, Cancelled |
| `rejection_reason` | TEXT | NULLABLE | Explanation if rejected |
| `approval_date` | VARCHAR(10) | NULLABLE | Date approved (YYYY-MM-DD) |
| `balance_used` | INTEGER | NOT NULL | Days deducted from balance |
| `attachments` | JSON | NOT NULL, DEFAULT '[]' | List of attachment file paths |

**Indexes:**
- Primary key index on `id`
- Index on `employee_id` (foreign key)

**Foreign Keys:**
- `employee_id` → `employees.id`

---

### 2.5. `attendance_logs` Table
**Purpose:** Daily attendance check-in/check-out records

**SQLAlchemy Model:**
```python
class AttendanceLogModel(Base):
    __tablename__ = "attendance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(50), ForeignKey("employees.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=True)
    status = Column(String(20), default='Present', nullable=False)  # 'Present', 'Absent', 'Late'

    # Relationships
    employee = relationship("EmployeeModel", back_populates="attendance_logs")
```

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid.uuid4() | Unique log identifier |
| `employee_id` | VARCHAR(50) | FOREIGN KEY(employees.id), NOT NULL, INDEX | Employee ID |
| `date` | VARCHAR(10) | NOT NULL, INDEX | Date of attendance (YYYY-MM-DD) |
| `check_in` | TIMESTAMP | NOT NULL | Check-in timestamp |
| `check_out` | TIMESTAMP | NULLABLE | Check-out timestamp |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'Present' | Status: Present, Absent, Late |

**Indexes:**
- Primary key index on `id`
- Index on `employee_id` (foreign key)
- Index on `date` (for date range queries)

**Foreign Keys:**
- `employee_id` → `employees.id`

---

### 2.6. `email_settings` Table
**Purpose:** SMTP email configuration (singleton table)

**SQLAlchemy Model:**
```python
class EmailSettingsModel(Base):
    __tablename__ = "email_settings"

    id = Column(Integer, primary_key=True, default=1)  # Only one record
    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False)
    smtp_username = Column(String(255), nullable=False)
    smtp_password_hash = Column(String(255), nullable=False)
    sender_email = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
```

**Columns:**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, DEFAULT 1 | Always 1 (singleton) |
| `smtp_host` | VARCHAR(255) | NOT NULL | SMTP server hostname |
| `smtp_port` | INTEGER | NOT NULL | SMTP server port |
| `smtp_username` | VARCHAR(255) | NOT NULL | SMTP username |
| `smtp_password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed SMTP password |
| `sender_email` | VARCHAR(255) | NOT NULL | "From" email address |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT FALSE | Global email toggle |

**Note:** This table should only ever have one row (ID=1)

---

## 3. Entity Relationships

```
users (1) ←→ (1) employees
    ↓
employee.user_id → users.id

units (1) ←→ (Many) employees
    ↓
employee.unit_id → units.id

employees (1) ←→ (Many) employees (Manager Hierarchy)
    ↓
employee.manager_id → employees.id

employees (1) ←→ (Many) leave_requests
    ↓
leave_request.employee_id → employees.id

employees (1) ←→ (Many) attendance_logs
    ↓
attendance_log.employee_id → employees.id
```

---

## 4. Database Initialization

### Default Unit Creation
When `init_db()` is called, it automatically creates a default "Administration" unit (ID: 1) if it doesn't exist. This ensures that the first admin user can be assigned to a valid unit.

```python
def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

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
    finally:
        db.close()

    print("[SUCCESS] Database tables created successfully!")
```

---

## 5. Repository Layer

All database access goes through repository classes in `backend/db_repositories.py`:

- **DBUserRepository**: User CRUD operations
- **DBEmployeeRepository**: Employee profile management
- **DBLeaveRequestRepository**: Leave request operations
- **DBUnitRepository**: Unit management
- **DBAttendanceRepository**: Attendance logging
- **DBEmailSettingsRepository**: Email configuration

### Example Repository Method
```python
class DBEmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, employee_id: str) -> Optional[Employee]:
        db_emp = self.db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
        if db_emp:
            return Employee(
                id=db_emp.id,
                user_id=str(db_emp.user_id),
                first_name_ar=db_emp.first_name_ar,
                last_name_ar=db_emp.last_name_ar,
                # ... map other fields
            )
        return None
```

---

## 6. Migration Notes

### Key Differences from CSV Implementation
1. **Type Safety**: Database enforces column types (no more leading zero issues)
2. **Foreign Keys**: Referential integrity guaranteed at DB level
3. **Transactions**: All operations wrapped in ACID transactions
4. **Concurrent Access**: PostgreSQL handles row-level locking automatically
5. **Indexing**: Faster lookups on foreign keys and frequently queried columns

### Common Issues During Migration
- **Empty String vs NULL**: Manager_id must be NULL (not empty string) for employees without managers
- **Auto-increment Sequences**: Don't manually set IDs when using SERIAL columns
- **Foreign Key Violations**: Ensure referenced records exist before inserting (e.g., unit must exist before creating employee)

---

## 7. Database Maintenance

### Backup Database
```bash
docker exec iau-portal-postgres pg_dump -U iau_admin iau_portal > backup.sql
```

### Restore Database
```bash
docker exec -i iau-portal-postgres psql -U iau_admin iau_portal < backup.sql
```

### Clear All Data (Reset)
```bash
docker exec -it iau-portal-backend python -c "from backend.database import drop_all_tables, init_db; drop_all_tables(); init_db()"
```

### Connect to PostgreSQL CLI
```bash
docker exec -it iau-portal-postgres psql -U iau_admin -d iau_portal
```

---

## 8. Future Enhancements

### Planned Schema Changes
- **Audit Logging Table**: Track all user actions
- **Notification Queue Table**: Store pending email notifications
- **Settings Table**: Application-wide configuration

### Database Migration Tool
- **Alembic** is installed but not yet configured
- Future schema changes will use Alembic migrations instead of manual updates

---

**Schema Version:** 1.0
**Last Schema Change:** January 3, 2026 (PostgreSQL migration)
**Next Planned Change:** Audit logging table
