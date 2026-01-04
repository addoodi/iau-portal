# IAU Portal: Development History & Technical Guide

> **Purpose:** This document serves as the detailed technical development history and implementation guide for the IAU Portal project, complementing CLAUDE.md's architectural overview.

**Last Updated:** 2026-01-04
**Project Status:** Production-Ready - PostgreSQL Migration Complete
**Current Version:** 1.0.0

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Implemented Features](#3-implemented-features)
4. [Development History](#4-development-history)
5. [Database Migration (CSV → PostgreSQL)](#5-database-migration)
6. [Current Architecture](#6-current-architecture)
7. [Deployment Guide](#7-deployment-guide)
8. [Known Issues & Limitations](#8-known-issues--limitations)

---

## 1. Project Overview

The IAU Portal is a comprehensive employee management system designed for the Institute of Innovation and Entrepreneurship at Imam Abdulrahman Bin Faisal University. It digitizes vacation requests, approvals, attendance tracking, and document generation with **full bilingual support (Arabic/English)**.

### Core Capabilities
- Leave request submission and approval workflow
- Automated vacation balance calculation with contract periods
- Digital signature management
- Real-time attendance tracking
- Automated document generation (DOCX with Hijri calendar)
- Email notifications (SMTP integration)
- Hierarchical team management
- Role-based access control (Admin, Dean, Manager, Employee)

---

## 2. Technology Stack

### Frontend
- **React 19.2.0** - Latest stable release
- **Vite 7.3.0** - Modern build tool (migrated from Create React App Dec 2025)
- **Tailwind CSS 3.4.17** - Utility-first styling with RTL support
- **React Router 7.10.1** - Client-side routing
- **Context API** - State management (PortalContext)
- **lucide-react** - Icon library
- **recharts** - Dashboard analytics

### Backend
- **FastAPI** - High-performance Python web framework
- **Pydantic** - Data validation and serialization
- **SQLAlchemy 2.0+** - ORM for PostgreSQL
- **psycopg2-binary** - PostgreSQL adapter
- **python-docx / docxtpl** - DOCX document generation
- **hijri-converter** - Hijri/Gregorian calendar conversion
- **bcrypt** - Password hashing
- **python-jose** - JWT token generation
- **pandas** - Legacy CSV handling (migration complete)

### Database
- **PostgreSQL 16 Alpine** - Production database (migrated Jan 2026)
- **Alembic** - Database migration tool (installed, not yet used)
- **ACID Transactions** - Data integrity guaranteed

### Infrastructure
- **Docker & Docker Compose** - Containerized deployment
- **Nginx** - Reverse proxy (frontend container)
- **Portainer** - Container management UI

---

## 3. Implemented Features

### 3.1. Authentication & Security
- **JWT-based Authentication**: Secure token-based auth with refresh
- **Password Hashing**: Bcrypt with salt
- **Role-Based Access Control**: Admin, Dean, Manager, Employee roles
- **First-Time Setup Flow**: Guided admin initialization
- **Password Change**: Secure password update via Profile page

### 3.2. User Management (Admin)
- **Create Users**: Email, password, role, bilingual names/positions
- **Edit Users**: Update all employee and user fields
- **Delete Users**: Remove users and associated employee records
- **Manager Assignment**: Hierarchical reporting structure
- **Unit Assignment**: Organize employees by department
- **Configurable Vacation Rates**: Custom monthly accrual per employee

### 3.3. Unit Management
- **CRUD Operations**: Create, Read, Update units
- **Bilingual Names**: English and Arabic unit names
- **Delete Protection**: Prevents deletion of units with assigned employees
- **Hierarchical Display**: Tree view of organizational structure

### 3.4. Leave Management
- **Request Types**: Annual, Sick, Emergency, Exams
- **Submission**: Date range, duration calculation, reason, attachments
- **Approval Workflow**:
  - Managers approve/reject team requests
  - Deans see all requests
  - Admins have full access
- **Conflict Detection**: Automatic overlap warnings for managers
- **Attachment Support**: Upload/download medical notes, etc.
- **Rejection Reasons**: Mandatory explanation for denied requests
- **Balance Validation**: Shows warnings for negative balance requests
- **Cancellation**: Employees can cancel pending requests
- **Document Download**: Auto-generated DOCX forms for approved requests

### 3.5. Vacation Balance System
- **Contract-Based Calculation**: 11-month auto-renewing contracts
- **Monthly Accrual**: Configurable rate (default: 2.5 days/month)
- **Automatic Renewal**: Balance resets at contract end
- **Negative Balance Support**: Allows requests exceeding balance with manager approval
- **Real-Time Updates**: Balance recalculated on approval/rejection

### 3.6. Attendance Tracking
- **Check-In/Out**: Daily attendance logging
- **Real-Time Status**: Present/Absent/Late indicators
- **Dashboard Widget**: Quick access from main dashboard
- **History Logging**: All attendance stored in `attendance_logs` table

### 3.7. Digital Signatures
- **Upload**: Image upload via Profile page
- **Secure Storage**: Stored in backend/data/signatures/
- **Auto-Include**: Signatures embedded in generated documents
- **Dual Signatures**: Employee + Manager signatures on forms

### 3.8. Document Generation
- **Template-Based**: DOCX templates with Jinja2 placeholders
- **Bilingual**: Arabic content with Hijri dates
- **Auto-Population**: Employee, manager, request details
- **Signature Integration**: Embedded signature images
- **Download**: Direct download from My Requests/Approvals pages

### 3.9. Email Notifications
- **SMTP Configuration**: UI-based setup (Site Settings)
- **Mailtrap Integration**: Development email testing
- **Production Ready**: SMTP_ENABLED environment variable
- **Future**: Automated notifications planned

### 3.10. Manager Features
- **Team Timeline**: 60-day calendar view of team availability
- **Dashboard Reports**: Downloadable DOCX team reports
- **Contract Management**: Update employee start dates
- **Conflict Alerts**: Visual warnings for overlapping requests
- **Unit Filtering**: Filter timeline by organizational unit

### 3.11. Dean Role
- **Special Manager**: Dean role functions as super-manager
- **Full Visibility**: See all employees and requests
- **Unit Filtering**: Filter by department
- **Timeline Access**: Full team calendar access

### 3.12. Bilingual Support
- **Complete Localization**: All UI text in English/Arabic
- **RTL Layout**: Automatic right-to-left for Arabic
- **Calendar Toggle**: Switch between Gregorian/Hijri display
- **translations.js**: Centralized translation management
- **Dynamic Rendering**: `lang` context switches display

### 3.13. Admin Tools
- **Site Settings**: Email configuration and testing
- **User Management**: Comprehensive user CRUD
- **Dashboard Analytics**: Team overview and reports
- **Contract Warnings**: 40-day expiration alerts

---

## 4. Development History

### Phase 1: Foundation (Dec 2024)
- Initial React + FastAPI setup
- CSV-based persistence
- Basic authentication (JWT)
- Simple leave request flow
- First bilingual implementation

### Phase 2: Feature Expansion (Dec 2024)
- User Management (Add/Edit/Delete)
- Unit Management
- Attendance tracking
- Digital signatures
- Document generation with docxtpl
- Email infrastructure (mock mode)
- Manager hierarchy
- Conflict detection

### Phase 3: Refinements (Dec 2024)
- IAU theme implementation (official colors/logo)
- Navigation redesign (HorizontalNav + HeaderBanner)
- Profile page improvements
- Dashboard analytics
- Contract period logic
- Attachment support for requests
- Rejection reason requirement

### Phase 4: Build System Modernization (Dec 2025)
- **CRA → Vite Migration** (Dec 27, 2025)
  - Removed 1,174 packages (react-scripts)
  - Build time: 30s+ → <5s
  - Dev server startup: 15s → <2s
  - Updated all import paths
  - Fixed index.html structure
  - Modernized package.json scripts

### Phase 5: PostgreSQL Migration (Jan 2026)
**Major Infrastructure Overhaul - All CSV files replaced with PostgreSQL**

#### Migration Timeline
- **Jan 2, 2026**: PostgreSQL decision made (over SQLite)
- **Jan 2-3, 2026**: Complete backend migration
- **Jan 3, 2026**: Deployment and testing
- **Jan 4, 2026**: Production deployment successful

#### Changes Implemented
1. **Database Setup**
   - Added PostgreSQL 16 Alpine container to docker-compose.yml
   - Created .env configuration with database credentials
   - Set up persistent volume for data storage

2. **Backend Migration**
   - Created `backend/database.py` with SQLAlchemy models
   - Created `backend/db_repositories.py` (PostgreSQL-backed repositories)
   - Updated `backend/dependencies.py` to use DB repositories
   - Updated `backend/main.py` to initialize database on startup
   - Installed SQLAlchemy, psycopg2-binary, alembic

3. **Schema Changes**
   - All models now use SQLAlchemy ORM
   - UUID primary keys for users
   - Auto-incrementing IDs for leave requests, units
   - Foreign key constraints enforced at database level
   - Proper indexing on foreign keys and lookup columns

4. **Bug Fixes During Migration**
   - Fixed foreign key violations for unit_id (default unit creation)
   - Fixed empty string manager_id issue (convert to NULL)
   - Fixed employee update signature mismatch
   - Fixed leave request update signature mismatch
   - Added auto-increment sequence fixes

5. **Features Added Post-Migration**
   - Profile navigation (user icon in header)
   - Attachment downloads with authentication
   - Dean role timeline access
   - Negative balance request support
   - Manager report contract period improvements
   - Rejection mark in document templates

6. **Health Check Fixes**
   - Installed curl in Docker containers
   - Fixed backend health check (replaced python requests)
   - Fixed frontend health check (replaced wget)
   - All containers now show "healthy" status

7. **Repository Cleanup**
   - Removed Examples folder and 254 unused files
   - Updated .gitignore for cleaner repository
   - Removed outdated documentation files
   - Kept only production-relevant files

#### Migration Statistics
- **Files Changed**: 50+ files
- **Lines of Code**: +5,000 lines (new DB layer)
- **Test Workflow**: Admin init → Units → Users → Requests → Approvals → Downloads (all successful)
- **Data Integrity**: ACID transactions, foreign key constraints
- **Performance**: Sub-second queries, connection pooling

---

## 5. Database Migration

### Before (CSV Files)
```
backend/data/
├── users.csv              # 500 bytes, race conditions
├── employees.csv          # 2KB, type conversion errors
├── leave_requests.csv     # 1KB, file locking issues
├── units.csv             # 300 bytes
├── attendance_logs.csv   # 500 bytes
└── email_settings.csv    # 200 bytes
```

**Problems:**
- File locking on Windows
- Race conditions (concurrent writes)
- Type conversion errors (leading zeros stripped)
- No foreign key constraints
- No transactions
- Data corruption risk
- Manual backup required

### After (PostgreSQL)
```
PostgreSQL Database: iau_portal
Tables:
├── users                 # UUID primary keys
├── employees             # String IDs with constraints
├── leave_requests        # Auto-increment IDs
├── units                 # Auto-increment IDs
├── attendance_logs       # UUID primary keys
└── email_settings        # Singleton table
```

**Benefits:**
- ✅ ACID transactions
- ✅ Foreign key constraints
- ✅ Concurrent access (row-level locking)
- ✅ Type safety (enforced at DB level)
- ✅ Automatic backups (pg_dump)
- ✅ Connection pooling
- ✅ Query optimization
- ✅ Referential integrity

### Database Schema (PostgreSQL)

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- 'admin', 'dean', 'manager', 'employee'
    is_active BOOLEAN DEFAULT TRUE
);
```

#### Employees Table
```sql
CREATE TABLE employees (
    id VARCHAR(50) PRIMARY KEY,  -- 'IAU-001' or '0000001'
    user_id UUID UNIQUE NOT NULL REFERENCES users(id),
    first_name_ar VARCHAR(100) NOT NULL,
    last_name_ar VARCHAR(100) NOT NULL,
    first_name_en VARCHAR(100) NOT NULL,
    last_name_en VARCHAR(100) NOT NULL,
    position_ar VARCHAR(200) NOT NULL,
    position_en VARCHAR(200) NOT NULL,
    unit_id INTEGER REFERENCES units(id),
    manager_id VARCHAR(50) REFERENCES employees(id),
    start_date VARCHAR(10) NOT NULL,  -- YYYY-MM-DD
    monthly_vacation_earned FLOAT DEFAULT 2.5,
    signature_path VARCHAR(500),
    contract_auto_renewed BOOLEAN DEFAULT FALSE
);
```

#### Leave Requests Table
```sql
CREATE TABLE leave_requests (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) REFERENCES employees(id),
    vacation_type VARCHAR(50) NOT NULL,
    start_date VARCHAR(10) NOT NULL,
    end_date VARCHAR(10) NOT NULL,
    duration INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    rejection_reason TEXT,
    approval_date VARCHAR(10),
    balance_used INTEGER NOT NULL,
    attachments JSON DEFAULT '[]'
);
```

#### Units Table
```sql
CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    name_en VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200) NOT NULL
);
```

#### Attendance Logs Table
```sql
CREATE TABLE attendance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id VARCHAR(50) REFERENCES employees(id),
    date VARCHAR(10) NOT NULL,
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Present'
);
```

#### Email Settings Table
```sql
CREATE TABLE email_settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    smtp_host VARCHAR(255) NOT NULL,
    smtp_port INTEGER NOT NULL,
    smtp_username VARCHAR(255) NOT NULL,
    smtp_password_hash VARCHAR(255) NOT NULL,
    sender_email VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE
);
```

---

## 6. Current Architecture

### Application Flow

```
User Browser
    ↓
Nginx (Frontend Container :80)
    ↓
React SPA (Vite build)
    ↓
API Calls (/api/*)
    ↓
FastAPI Backend Container (:8000)
    ↓
SQLAlchemy ORM
    ↓
PostgreSQL Container (:5432)
    ↓
Persistent Volume
```

### Repository Pattern

```
API Endpoint (main.py)
    ↓
Service Layer (services.py)
    ↓
Repository Interface
    ├─ DBUserRepository
    ├─ DBEmployeeRepository
    ├─ DBLeaveRequestRepository
    ├─ DBUnitRepository
    ├─ DBAttendanceRepository
    └─ DBEmailSettingsRepository
    ↓
SQLAlchemy Models (database.py)
    ↓
PostgreSQL Database
```

### Dependency Injection

```python
# backend/dependencies.py
def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    employee_repo = DBEmployeeRepository(db)
    user_repo = DBUserRepository(db)
    leave_request_repo = DBLeaveRequestRepository(db)
    return EmployeeService(employee_repo, user_repo, leave_request_repo)
```

---

## 7. Deployment Guide

### Docker Compose Deployment

```bash
# Clone repository
git clone https://github.com/addoodi/iau-portal.git
cd iau-portal

# Start all services
docker-compose up -d

# Services:
# - frontend: http://localhost:3000
# - backend: http://localhost:8000
# - postgres: localhost:5432
```

### Environment Variables (.env)
```env
# PostgreSQL
POSTGRES_DB=iau_portal
POSTGRES_USER=iau_admin
POSTGRES_PASSWORD=iau_secure_password_2024
POSTGRES_PORT=5432

# Backend
DATABASE_URL=postgresql://iau_admin:iau_secure_password_2024@postgres:5432/iau_portal

# SMTP (optional)
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_SENDER_EMAIL=noreply@iau-portal.com
SMTP_ENABLED=true
```

### Local Development

**Backend:**
```bash
# Set DATABASE_URL for localhost
export DATABASE_URL=postgresql://iau_admin:iau_secure_password_2024@localhost:5432/iau_portal

# Run backend
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend:**
```bash
npm install
npm run dev  # Vite dev server
```

### Database Management

**Initialize Database:**
```bash
docker exec -it iau-portal-backend python -c "from backend.database import init_db; init_db()"
```

**Backup Database:**
```bash
docker exec iau-portal-postgres pg_dump -U iau_admin iau_portal > backup.sql
```

**Restore Database:**
```bash
docker exec -i iau-portal-postgres psql -U iau_admin iau_portal < backup.sql
```

**Clear Database:**
```bash
docker exec -it iau-portal-backend python -c "from backend.database import drop_all_tables, init_db; drop_all_tables(); init_db()"
```

---

## 8. Known Issues & Limitations

### Resolved Issues
- ✅ CSV file locking (migrated to PostgreSQL)
- ✅ Race conditions (ACID transactions)
- ✅ Type conversion errors (enforced schemas)
- ✅ CRA deprecation (migrated to Vite)
- ✅ Health check failures (fixed with curl)
- ✅ Attachment download 401 errors (added authentication)
- ✅ Profile access missing (added to navigation)

### Current Limitations
- **No Automated Tests**: Testing is manual (pytest/RTL not implemented)
- **No Real-Time Updates**: Requires manual refresh (WebSocket planned)
- **No Audit Logging**: Actions not tracked (planned for compliance)
- **Email Notifications**: Infrastructure ready but not automated
- **Single Language UI**: Can switch, but not per-user preference
- **No Conflict Prevention**: Only warnings, doesn't block overlapping requests

### Future Enhancements
- Automated testing (pytest + React Testing Library)
- Real-time notifications (WebSocket)
- Audit logging (who did what, when)
- Advanced reporting (Excel exports)
- PWA support (offline access)
- Bulk operations (approve multiple requests)
- Email templates (prettier HTML emails)

---

## 9. Key Development Decisions

### Why PostgreSQL over SQLite?
- ✅ Better for production deployments
- ✅ University IT familiar with PostgreSQL
- ✅ Better concurrent access handling
- ✅ More robust for 50-100 users

### Why Vite over Create React App?
- ✅ CRA is deprecated (no updates since 2023)
- ✅ 10-100x faster builds
- ✅ Modern ESM-based architecture
- ✅ Better dev experience

### Why Context API over Redux?
- ✅ Simpler for solo developer
- ✅ Sufficient for app scale
- ✅ Built-in to React
- ✅ Less boilerplate

### Why FastAPI over Django/Flask?
- ✅ Modern async support
- ✅ Automatic API documentation
- ✅ Type safety with Pydantic
- ✅ High performance

---

## 10. File Structure

```
iau-portal/
├── backend/
│   ├── data/                      # Persistent data volume
│   │   ├── signatures/           # User signature images
│   │   └── attachments/          # Request attachments
│   ├── templates/
│   │   └── vacation_template.docx
│   ├── __init__.py
│   ├── main.py                   # FastAPI app + endpoints
│   ├── models.py                 # Pydantic models
│   ├── database.py               # SQLAlchemy ORM models
│   ├── db_repositories.py        # PostgreSQL repositories
│   ├── services.py               # Business logic
│   ├── auth.py                   # JWT authentication
│   ├── dependencies.py           # Dependency injection
│   ├── calculation.py            # Balance calculations
│   ├── document_generator.py     # DOCX generation
│   └── email_service.py          # SMTP email
├── src/
│   ├── components/               # React components
│   │   ├── HorizontalNav.jsx
│   │   ├── HeaderBanner.jsx
│   │   ├── RequestModal.jsx
│   │   └── ...
│   ├── pages/                    # Page components
│   │   ├── Dashboard.jsx
│   │   ├── MyRequests.jsx
│   │   ├── Approvals.jsx
│   │   ├── UserManagement.jsx
│   │   └── ...
│   ├── context/
│   │   └── PortalContext.jsx    # Global state
│   ├── utils/
│   │   └── translations.js      # Bilingual strings
│   ├── assets/
│   │   └── images/
│   ├── api.js                   # Backend HTTP client
│   ├── App.jsx                  # Main app component
│   └── index.jsx                # React entry point
├── public/
│   └── index.html
├── docker-compose.yml           # Container orchestration
├── Dockerfile.backend           # Backend container
├── Dockerfile.frontend          # Frontend container
├── nginx.conf                   # Nginx reverse proxy
├── requirements.txt             # Python dependencies
├── package.json                 # Node dependencies
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind CSS config
├── CLAUDE.md                    # AI assistant context
├── Gemini.md                    # This file
├── Gemini-database.md           # Database schema reference
├── form-guide.md                # Document template guide
└── README.md                    # Project readme
```

---

## 11. Critical Instructions for AI Assistants

### Documentation Maintenance
1. **ALWAYS update this file** (`Gemini.md`) when making significant changes
2. **Update CLAUDE.md** for architectural changes
3. **Update Gemini-database.md** when modifying database schema
4. **Update form-guide.md** when adding template placeholders

### Localization Requirements
1. **ALL user-facing text MUST be bilingual**
2. **Use `src/utils/translations.js`** for all strings
3. **Provide Arabic translation** for every English string
4. **Test RTL layout** for Arabic display
5. **Use `lang` context** to switch between languages

### Code Quality Standards
1. **Follow Repository Pattern** for data access
2. **Use Pydantic models** for API validation
3. **Maintain separation**: Pages → Components → Context → API
4. **Use JWT authentication** for protected endpoints
5. **Handle errors gracefully** with user-friendly messages

### Database Changes
1. **Never modify database.py** without updating Gemini-database.md
2. **Always use foreign key constraints** for relationships
3. **Test with fresh database** after schema changes
4. **Provide migration scripts** for schema changes

---

**Status:** ✅ Production-Ready
**Last Deployment:** January 4, 2026
**Next Steps:** Audit logging, automated testing, real-time notifications

---

**Built with [Claude Code](https://claude.com/claude-code)**
