# CLAUDE.md - IAU Portal Development Context

> **Purpose:** This file provides complete context for AI coding assistants (Claude, GPT, Gemini, etc.) and serves as the technical handover guide for university IT staff.

**Last Updated:** 2026-01-05
**Project Status:** Pilot Phase - Phase 2 Complete, Production Security Hardening Complete
**Current Version:** 0.3.0 (Security Hardened)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack & Rationale](#2-tech-stack--rationale)
3. [Architecture](#3-architecture)
4. [Critical Constraints](#4-critical-constraints)
5. [Development Principles](#5-development-principles)
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [Technical Debt & Known Issues](#7-technical-debt--known-issues)
8. [Development Workflow](#8-development-workflow)
9. [Handover Strategy](#9-handover-strategy)
10. [Key Decisions Log](#10-key-decisions-log)

---

## 1. Project Overview

### 1.1 Mission Statement

The IAU Portal is an employee leave management system for the Institute of Innovation and Entrepreneurship at Imam Abdulrahman Bin Faisal University (IAU). The system digitizes vacation requests, approvals, attendance tracking, and document generation with **full bilingual support (Arabic/English)**.

### 1.2 Core User Flows (Must-Haves)

| Priority | Flow | Status |
|----------|------|--------|
| **CRITICAL** | Leave request submission/approval | ✅ Implemented |
| **CRITICAL** | Document generation (vacation forms) | ✅ Implemented |
| **CRITICAL** | User/unit management | ✅ Implemented |
| **CRITICAL** | Analytics dashboard | ✅ Implemented (needs enhancement) |
| **CRITICAL** | Email notifications | ✅ Infrastructure ready |
| **CRITICAL** | Mobile-responsive access | ✅ Implemented |
| **IMPORTANT** | Attendance tracking (calculated) | ✅ Implemented |
| **NICE-TO-HAVE** | Real-time dashboard updates | ⏳ Planned (Phase 4) |

### 1.3 Scale & Performance Requirements

- **Current Users:** 10s of employees
- **12-Month Projection:** 50-100 employees
- **Peak Concurrent Users:** ~10
- **Acceptable Page Load Time:** <3 seconds
- **Expected Uptime:** Best effort (99%+ target)
- **Leave Requests per Month:** 10s

### 1.4 Deployment Context

- **Current Environment:** Solo developer local machine (Windows)
- **Target Environment:** University on-premises server (Windows/Linux unknown)
- **Handover Timeline:** 6-12 months pilot, then production
- **Development Velocity:** ~4 hours/week
- **Team Size:** 1 developer (junior/mid-level, learning as building)

---

## 2. Tech Stack & Rationale

### 2.1 Current Stack (As Implemented)

#### Frontend
```
React 19.2.0          ← Latest stable (good choice)
Vite 7.3.0            ← ✅ Modern build tool (migrated 2025-12-27)
Tailwind CSS 3.4.17   ← Modern, maintainable
React Router 7.10.1   ← Standard routing
Context API           ← Built-in state management
lucide-react          ← Icon library
recharts              ← Dashboard charts
```

#### Backend
```
FastAPI               ← Excellent choice (modern, fast, Python)
Pydantic              ← Type validation (great)
Uvicorn               ← ASGI server
JWT (python-jose)     ← Secure authentication
Pandas                ← CSV data manipulation
docxtpl               ← Document generation
hijri-converter       ← Arabic calendar support
```

#### Data Storage
```
CSV files via Pandas  ← TEMPORARY (must migrate to database)
```

#### Testing
```
Jest + React Testing Library  ← Installed but UNUSED (0% coverage)
pytest                        ← NOT installed yet
```

#### Deployment
```
Windows batch files   ← TEMPORARY (must containerize)
No CI/CD              ← Planned
No Git                ← CRITICAL: Must initialize immediately
```

---

### 2.2 Approved Tech Stack (Post-Migration)

#### ✅ **VALIDATED STACK (Keep These)**

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Frontend Framework** | React 19 | ✅ Modern, well-supported, team has experience |
| **Backend Framework** | FastAPI (Python) | ✅ Excellent choice - fast, type-safe, great docs |
| **Styling** | Tailwind CSS | ✅ Utility-first, responsive, easy maintenance |
| **Authentication** | JWT (python-jose) | ✅ Stateless, secure, industry standard |
| **Document Generation** | docxtpl + python-docx | ✅ Works well, meets requirements |
| **Bilingual Support** | Custom translations.js + RTL | ✅ Working, no need to change |
| **UI Components** | Lucide React icons | ✅ Clean, lightweight |
| **Charts** | Recharts | ✅ Good for dashboards |

#### 🔄 **PLANNED MIGRATIONS (Technical Debt Reduction)**

| Migration | From | To | Priority | Effort | Rationale |
|-----------|------|----|----|--------|-----------|
| **Build System** | Create React App | **Vite** | 🔴 HIGH | 2-3 hrs | CRA deprecated (dead since 2023), Vite 10-100x faster, easier handover |
| **Database** | CSV files | **SQLite → PostgreSQL** | 🔴 HIGH | 6 hrs (SQLite) | CSV = data corruption risk, no transactions, not production-safe |
| **Version Control** | None | **Git + GitHub** | 🔴 CRITICAL | 1 hr | Can't track changes, collaborate, or revert without Git |
| **Deployment** | Batch files | **Docker + docker-compose** | 🟡 MEDIUM | 3 hrs | Professional handover, IT-friendly, cross-platform |
| **Testing** | None (0%) | **Critical path tests (pytest + RTL)** | 🟡 MEDIUM | 4 hrs | Safety net for auth, approvals, balance calculations |
| **Type Safety** | JavaScript | **Keep JavaScript** | ⚪ REJECTED | N/A | TypeScript = too much learning curve for solo dev |

#### ❌ **REJECTED ALTERNATIVES (Don't Do These)**

| Technology | Why Rejected |
|------------|--------------|
| TypeScript | Too steep learning curve for solo dev with 4 hrs/week |
| Next.js | Unnecessary complexity - SPA is sufficient |
| Redux/Zustand | Context API is working fine, no need to add complexity |
| GraphQL | REST API is adequate for this scale |
| Native Mobile Apps | Responsive web app sufficient (PWA possible later) |
| Microservices | Overkill for 10-100 users |
| NoSQL (MongoDB) | SQL better for relational data (employees → managers → units) |

---

### 2.3 Database Strategy (Phased Approach)

**Phase 1 (Current):** CSV files via Pandas
**Phase 2 (Weeks 3-4):** **SQLite** (file-based, zero setup, ACID guarantees)
**Phase 3 (Production):** **PostgreSQL** (when scaling beyond 50 users or deploying to university IT)

**Why SQLite First?**
- ✅ Zero infrastructure setup (single file like CSV)
- ✅ ACID transactions (no data corruption)
- ✅ University IT can understand/manage it
- ✅ SQLAlchemy ORM makes PostgreSQL migration a connection string change
- ✅ Built-in backup/restore tools

**Migration Path:**
```python
# Phase 2: CSV → SQLite (keep same API)
# Phase 3: SQLite → PostgreSQL (change connection string only)
DATABASE_URL = "sqlite:///data/iau_portal.db"  # Phase 2
DATABASE_URL = "postgresql://user:pass@host/db"  # Phase 3
```

---

## 3. Architecture

### 3.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    IAU Portal (Browser)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React 19 SPA (Port 3000)                            │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │  Pages/    │  │  Components/ │  │  Context/   │  │  │
│  │  │  Routes    │→ │  Modals      │→ │  Portal     │  │  │
│  │  └────────────┘  └──────────────┘  └─────────────┘  │  │
│  │         ↓                ↓                 ↓          │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │      api.js (REST Client)                     │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └────────────────────┬─────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────┘
                         │ HTTP/JSON
                         │ JWT Bearer Token
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  FastAPI Backend (Port 8000)                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  main.py (API Endpoints)                             │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │  /api/     │  │  /api/       │  │  /api/      │  │  │
│  │  │  auth      │  │  employees   │  │  requests   │  │  │
│  │  └────────────┘  └──────────────┘  └─────────────┘  │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               ↓                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  services.py (Business Logic)                        │  │
│  │  - EmployeeService, LeaveRequestService, etc.       │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               ↓                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  repositories.py (Data Access)                       │  │
│  │  - CSVUserRepository, CSVEmployeeRepository          │  │
│  └────────────┬─────────────────────────────────────────┘  │
│               ↓                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Storage (backend/data/)                        │  │
│  │  - users.csv, employees.csv, leave_requests.csv      │  │
│  │  - units.csv, attendance_logs.csv                    │  │
│  │  - signatures/, attachments/                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

External Integrations:
┌────────────────┐      ┌────────────────┐
│  Email Server  │←─────│  document_     │
│  (SMTP)        │      │  generator.py  │
└────────────────┘      └────────────────┘
```

### 3.2 Backend Layered Architecture

**Pattern:** Repository → Service → Controller (API Endpoints)

```python
# Example Flow: Create Leave Request

# 1. API Endpoint (main.py)
@app.post("/api/requests")
def create_leave_request(
    request: LeaveRequestCreate,
    current_user: User = Depends(get_current_user)
):
    # 2. Calls Service Layer
    return leave_service.create_leave_request(request, current_user.id)

# 3. Service Layer (services.py) - Business Logic
class LeaveRequestService:
    def create_leave_request(self, data, user_id):
        # Calculate duration, validate balance
        employee = employee_repo.get_by_user_id(user_id)
        duration = (data.end_date - data.start_date).days
        new_request = LeaveRequest(...)

        # 4. Calls Repository Layer
        return leave_repo.add(new_request)

# 5. Repository Layer (repositories.py) - Data Access
class CSVLeaveRequestRepository:
    def add(self, leave_request):
        # Persist to CSV/Database
        df = pd.read_csv(self.file_path)
        # ... append and save
```

**Key Benefits:**
- ✅ Separation of concerns
- ✅ Easy to swap CSV → SQLite → PostgreSQL (only change repositories)
- ✅ Business logic reusable across endpoints
- ✅ Testable (can mock repositories)

### 3.3 Frontend Component Architecture

```
src/
├── pages/              ← Route-level components
│   ├── Dashboard.jsx
│   ├── MyRequests.jsx
│   ├── Approvals.jsx
│   └── UserManagement.jsx
├── components/         ← Reusable UI components
│   ├── Sidebar.jsx
│   ├── TopBar.jsx
│   ├── AddUserModal.jsx
│   └── RequestModal.jsx
├── context/            ← Global state
│   └── PortalContext.jsx  ← User session, data fetching, language
├── utils/
│   └── translations.js    ← Bilingual strings (AR/EN)
└── api.js              ← Backend HTTP client
```

**State Management Pattern:**
```javascript
// PortalContext provides:
const {
  user,              // Current logged-in user
  employees,         // All employees (admin only)
  requests,          // Leave requests
  units,             // Organizational units
  lang,              // 'ar' or 'en'
  login,             // Login function
  createRequest,     // Submit leave request
  updateRequest,     // Approve/reject
  refreshData        // Re-fetch from backend
} = usePortal();
```

---

## 4. Critical Constraints

### 4.1 Hard Requirements (Cannot Change)

| Constraint | Impact | Compliance |
|------------|--------|------------|
| **MUST remain bilingual (Arabic/English)** | All features, UI, documents | ✅ Implemented via translations.js + RTL CSS |
| **MUST support Arabic calendar (Hijri)** | Document dates, display | ✅ Implemented via hijri-converter |
| **MUST deploy on-premises (university server)** | No cloud hosting | ⏳ Planned via Docker |
| **MUST handle personal data securely** | Encryption at rest/transit, audit logs | ⚠️ Partial (JWT auth done, audit logs pending) |
| **MUST support mobile access** | Responsive design | ✅ Implemented via Tailwind responsive classes |

### 4.2 Soft Constraints (Preferences)

- **Prefer Python backend** (team has basic experience)
- **Prefer simple deployment** (university IT has limited DevOps expertise)
- **Prefer free/open-source tools** (budget constraint)
- **Prefer gradual migration** (pilot → production phased approach)

### 4.3 Developer Constraints

- **Solo developer:** 1 person, junior/mid skill level
- **Time availability:** ~4 hours/week
- **Background:** Minor Python/React experience, learning as building
- **No DevOps experience:** Needs simple, well-documented deployment
- **No TypeScript experience:** Stick to JavaScript

---

## 5. Development Principles

### 5.1 Core Philosophy

**"Balance speed and stability based on criticality"**

- ✅ Move fast on UI/UX iteration
- ✅ Move carefully on authentication, data integrity, balance calculations
- ✅ Catch bugs before users via critical path testing
- ✅ Document for future self and university IT

### 5.2 Code Quality Standards

#### **What We Enforce:**
- ✅ Pydantic type validation on all API inputs/outputs
- ✅ JWT authentication on all protected endpoints
- ✅ Bilingual support for ALL user-facing text
- ✅ Repository pattern for data access (easy database migration)
- ✅ Clear separation: Pages → Components → Context → API

#### **What We Don't Enforce (Yet):**
- ⚪ TypeScript (JavaScript is acceptable)
- ⚪ Strict linting/Prettier (basic ESLint only)
- ⚪ Comprehensive test coverage (focus on critical paths)
- ⚪ Code reviews (solo developer)

### 5.3 Security Requirements

| Category | Requirement | Status |
|----------|-------------|--------|
| **Authentication** | JWT tokens, secure password hashing (bcrypt) | ✅ Implemented |
| **Authorization** | Role-based access (admin/manager/employee/dean) | ✅ Implemented |
| **Data Encryption (Transit)** | HTTPS in production | ⏳ Deployment phase |
| **Data Encryption (At Rest)** | Database encryption | ⏳ SQLite/PostgreSQL migration |
| **Audit Logging** | Track user actions (create/approve/delete) | ⏳ Planned (Phase 3) |
| **Multi-Factor Auth (MFA)** | Optional 2FA | ❌ Not required |
| **CORS** | Restricted to university domain | ⚠️ Currently `*` (dev mode) |

### 5.4 Testing Strategy (Pragmatic)

**Philosophy:** Test the highest-risk features, not everything.

#### **MUST TEST (Critical Paths):**
1. **Authentication Flow**
   - ✅ Admin can log in with correct credentials
   - ✅ Login fails with wrong password
   - ✅ JWT token validation works
   - ✅ Protected endpoints reject unauthenticated requests

2. **Vacation Balance Calculation**
   - ✅ Balance = (months_worked × monthly_rate) - approved_days
   - ✅ Contract renewal resets balance correctly
   - ✅ Negative balance prevents approval

3. **Leave Approval Workflow**
   - ✅ Manager can approve direct report's request
   - ✅ Employee cannot approve own request
   - ✅ Balance deducted on approval
   - ✅ Approval sets status = "Approved" and timestamp

#### **NICE TO TEST (Lower Priority):**
- Unit management CRUD
- Attendance check-in/out
- Document generation (manual QA acceptable)

**Framework:** `pytest` (backend) + React Testing Library (frontend)
**Target Coverage:** 60-70% for critical paths (not 100%)

---

## 6. Implementation Roadmap

### 6.1 Phase 1: Foundation & Safety (WEEKS 1-2) 🔴 **IMMEDIATE**

**Goal:** Version control + backups to prevent data loss

| Task | Time | Priority | Status |
|------|------|----------|--------|
| Initialize Git repository | 30 min | CRITICAL | ⏳ Pending |
| Create comprehensive `.gitignore` | 15 min | CRITICAL | ⏳ Pending |
| Push to GitHub (private repo) | 15 min | CRITICAL | ⏳ Pending |
| Add README for university IT | 1 hr | HIGH | ⏳ Pending |
| Backup current CSV data | 15 min | CRITICAL | ⏳ Pending |
| Document current deployment process | 30 min | MEDIUM | ⏳ Pending |

**Deliverable:** Version-controlled codebase on GitHub with backup strategy

**Success Criteria:**
- ✅ Can revert any code change
- ✅ CSV data backed up externally
- ✅ University IT can clone and understand repo

---

### 6.2 Phase 2: Modernization (WEEKS 3-6) 🟠 **HIGH IMPACT**

**Goal:** Migrate to modern, maintainable stack

| Task | Time | Priority | Status |
|------|------|----------|--------|
| **Migrate CRA → Vite** | 2.5 hrs | HIGH | ✅ **COMPLETE** (2025-12-27) |
| - Install Vite and plugins | 15 min | | ✅ |
| - Create vite.config.js | 5 min | | ✅ |
| - Move & update index.html | 10 min | | ✅ |
| - Rename index.js to index.jsx | 2 min | | ✅ |
| - Update package.json scripts | 5 min | | ✅ |
| - Remove react-scripts (1,174 packages) | 10 min | | ✅ |
| - Update Tailwind config | 5 min | | ✅ |
| - Test dev server | 30 min | | ✅ |
| - Test production build | 15 min | | ✅ |
| - Commit and merge to main | 15 min | | ✅ |
| **Migrate CSV → SQLite** | 6 hrs | HIGH | ⏳ Pending |
| - Install SQLAlchemy | 15 min | | |
| - Create SQLAlchemy models | 2 hrs | | |
| - Write CSV→SQLite migration script | 2 hrs | | |
| - Update repositories | 1 hr | | |
| - Test thoroughly | 45 min | | |
| **Add Critical Path Tests** | 4 hrs | MEDIUM | ⏳ Pending |
| - Setup pytest + React Testing Library | 30 min | | |
| - Write auth tests | 1 hr | | |
| - Write balance calculation tests | 1 hr | | |
| - Write approval workflow tests | 1.5 hrs | | |

**Deliverable:** Modern stack (Vite + SQLite + tests) ready for production

**Success Criteria:**
- ✅ Build time <5 seconds (Vite vs. 30s+ with CRA)
- ✅ Data integrity guaranteed (SQLite ACID transactions)
- ✅ Critical bugs caught by tests before deployment

---

### 6.3 Phase 3: Production Readiness (WEEKS 7-12) 🟡 **FOR HANDOVER**

**Goal:** Professional deployment ready for university IT

| Task | Time | Priority | Status |
|------|------|----------|--------|
| **Create Docker Containers** | 3 hrs | HIGH | ⏳ Pending |
| - Write Dockerfile (frontend) | 45 min | | |
| - Write Dockerfile (backend) | 45 min | | |
| - Create docker-compose.yml | 30 min | | |
| - Test locally | 1 hr | | |
| **Write Handover Documentation** | 2 hrs | HIGH | ⏳ Pending |
| - Deployment guide (step-by-step) | 1 hr | | |
| - User manual (screenshots) | 1 hr | | |
| **Implement Audit Logging** | 3 hrs | MEDIUM | ⏳ Pending |
| - Create audit_logs table | 30 min | | |
| - Add logging to critical actions | 1.5 hrs | | |
| - Create admin audit viewer | 1 hr | | |
| **Create Manual QA Checklist** | 1 hr | MEDIUM | ⏳ Pending |
| - Login/logout scenarios | 15 min | | |
| - Leave request workflows | 20 min | | |
| - Document generation | 15 min | | |
| - Admin operations | 10 min | | |

**Deliverable:** Production-ready system with Docker + documentation

**Success Criteria:**
- ✅ University IT can deploy with `docker-compose up`
- ✅ All actions auditable (who did what, when)
- ✅ Non-technical staff can perform QA

---

### 6.4 Phase 4: Enhancements (WEEKS 13+) 🔵 **OPTIONAL**

**Goal:** Nice-to-have features if time permits

| Task | Time | Priority | Status |
|------|------|----------|--------|
| Real-time WebSocket updates | 5 hrs | LOW | ⏳ Planned |
| Migrate SQLite → PostgreSQL | 2 hrs | LOW | ⏳ Planned |
| Email notifications (live) | 3 hrs | LOW | ⏳ Planned |
| PWA (offline support) | 4 hrs | LOW | ⏳ Planned |
| Mobile app (React Native) | 40 hrs | REJECTED | ❌ Not feasible |

---

## 7. Technical Debt & Known Issues

### 7.1 Critical Technical Debt (Must Fix Before Production)

| Issue | Risk | Mitigation Plan | Target Phase |
|-------|------|-----------------|--------------|
| **No Git version control** | Data loss, cannot revert bugs | Initialize Git + GitHub | Phase 1 (Week 1) |
| **CRA is deprecated** | Security vulnerabilities, no updates | Migrate to Vite | Phase 2 (Week 3) |
| **CSV storage** | Data corruption, race conditions | Migrate to SQLite | Phase 2 (Week 4-5) |
| **No tests** | Breaking changes undetected | Critical path tests | Phase 2 (Week 6) |
| **No audit logs** | Cannot track malicious actions | Implement audit logging | Phase 3 (Week 9) |
| **CORS = `*`** | Security vulnerability | Restrict to university domain | Phase 3 (deployment) |

### 7.2 Medium-Priority Technical Debt

| Issue | Impact | Plan |
|-------|--------|------|
| No TypeScript | More runtime errors | **Accepted** - not worth migration cost |
| No Prettier/strict linting | Inconsistent code style | Low priority for solo dev |
| No CI/CD pipeline | Manual testing/deployment | Add GitHub Actions in Phase 3 |
| No monitoring/logging | Hard to debug production issues | Add in Phase 4 |
| No email notifications (live) | Users must check dashboard | Phase 4 enhancement |

### 7.3 Known Bugs & Limitations

**Current Known Issues:**
1. ⚠️ **Dashboard refresh loop** - Fixed via dependency array optimization
2. ⚠️ **Signature positioning in DOCX** - Requires manual template adjustment (user action required)
3. ⚠️ **No conflict detection** - Two employees can request same dates (low priority)
4. ⚠️ **No email reminders** - Managers must check dashboard for pending requests

**Accepted Limitations (By Design):**
- CSV storage (temporary, migrating to SQLite)
- No real-time updates (polling/WebSockets planned for Phase 4)
- No offline support (PWA planned for Phase 4)
- No mobile app (responsive web sufficient)

---

## 8. Development Workflow

### 8.1 Local Development Setup

**Prerequisites:**
- Node.js 18+ (for React frontend)
- Python 3.9+ (for FastAPI backend)
- Git (for version control)

**First-Time Setup:**
```bash
# 1. Clone repository (after Git initialization)
git clone https://github.com/YOUR_USERNAME/iau-portal.git
cd iau-portal

# 2. Install frontend dependencies
npm install

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Create .env file (backend)
# Add: SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, etc.

# 5. Run backend (terminal 1)
python -m uvicorn backend.main:app --reload
# → http://127.0.0.1:8000

# 6. Run frontend (terminal 2)
npm start
# → http://localhost:3000
```

**Daily Development:**
```bash
# Backend (FastAPI + auto-reload)
cd backend
python -m uvicorn main:app --reload

# Frontend (React + hot reload)
npm start
```

### 8.2 Project File Structure

```
iau-portal/
├── backend/
│   ├── data/                    ← CSV storage (temporary)
│   │   ├── users.csv
│   │   ├── employees.csv
│   │   ├── leave_requests.csv
│   │   ├── units.csv
│   │   ├── attendance_logs.csv
│   │   ├── signatures/          ← User signature images
│   │   └── attachments/         ← Request attachments
│   ├── templates/
│   │   └── vacation_template.docx
│   ├── main.py                  ← FastAPI app + API endpoints
│   ├── models.py                ← Pydantic models
│   ├── repositories.py          ← Data access layer
│   ├── services.py              ← Business logic
│   ├── auth.py                  ← JWT authentication
│   ├── dependencies.py          ← Dependency injection
│   ├── document_generator.py    ← DOCX generation
│   └── calculation.py           ← Balance calculations
├── src/
│   ├── components/              ← Reusable UI
│   ├── pages/                   ← Route components
│   ├── context/
│   │   └── PortalContext.jsx    ← Global state
│   ├── utils/
│   │   └── translations.js      ← Bilingual strings
│   ├── api.js                   ← Backend HTTP client
│   ├── App.jsx                  ← Main app + routing
│   └── index.css                ← Tailwind imports
├── public/
├── package.json
├── requirements.txt
├── tailwind.config.js
├── CLAUDE.md                    ← This file
├── Gemini.md                    ← Legacy development history
├── Gemini-database.md           ← Database schema docs
└── form-guide.md                ← Document template guide
```

### 8.3 Coding Conventions

**Backend (Python):**
```python
# Use type hints with Pydantic
class Employee(BaseModel):
    id: str
    first_name_ar: str
    vacation_balance: int

# Repository pattern
class CSVEmployeeRepository:
    def get_by_id(self, employee_id: str) -> Optional[Employee]:
        # ...

# Service layer for business logic
class EmployeeService:
    def __init__(self, repo: CSVEmployeeRepository):
        self.repo = repo

    def get_employee_with_balance(self, employee_id: str):
        # Calculate balance, return EmployeeWithBalance
```

**Frontend (JavaScript + React):**
```javascript
// Use functional components + hooks
const MyRequests = () => {
  const { user, requests, lang } = usePortal();

  // Bilingual display
  const name = lang === 'ar' ? user.name_ar : user.name_en;

  return <div>...</div>;
};

// Always provide bilingual text
const t = {
  en: "Submit Request",
  ar: "تقديم طلب"
};
```

**File Naming:**
- Components: `PascalCase.jsx` (e.g., `AddUserModal.jsx`)
- Utilities: `camelCase.js` (e.g., `translations.js`)
- Backend: `snake_case.py` (e.g., `document_generator.py`)

---

## 9. Handover Strategy (University IT)

### 9.1 Deployment Options for University

**Option A: Docker (Recommended)**
```bash
# University IT runs:
docker-compose up -d

# That's it! Application runs on:
# - Frontend: http://server-ip
# - Backend: http://server-ip:8000
```

**Option B: Manual Setup (If Docker Not Available)**
```bash
# 1. Install Python 3.9+, Node.js 18+
# 2. Clone repo
# 3. Install dependencies (npm install, pip install -r requirements.txt)
# 4. Configure .env
# 5. Run: npm run build && python -m uvicorn backend.main:app --host 0.0.0.0
```

### 9.2 University IT Handover Checklist

**Before Handover:**
- [ ] Migrate CSV → SQLite (Phase 2)
- [ ] Create Docker containers (Phase 3)
- [ ] Write deployment guide with screenshots
- [ ] Create user manual (Arabic + English)
- [ ] Test on university server (staging)
- [ ] Train 1-2 IT staff members
- [ ] Document backup/restore procedures
- [ ] Implement audit logging
- [ ] Set up monitoring alerts (optional)

**Handover Package Includes:**
1. Docker containers (docker-compose.yml)
2. Deployment guide (PDF, bilingual)
3. User manual (PDF, bilingual)
4. Database backup scripts
5. Troubleshooting FAQ
6. Contact info for developer (handover support period)

### 9.3 Production Environment Requirements

**Minimum Server Specs:**
- **OS:** Windows Server 2019+ OR Linux (Ubuntu 20.04+)
- **RAM:** 4 GB minimum, 8 GB recommended
- **Storage:** 20 GB (10 GB for app, 10 GB for data/logs)
- **CPU:** 2 cores minimum
- **Network:** Static IP, HTTPS certificate (Let's Encrypt)

**Required Software:**
- Docker + Docker Compose (recommended)
- OR: Python 3.9+, Node.js 18+, Nginx (if manual setup)

**Security Checklist:**
- [ ] HTTPS enabled (SSL certificate)
- [ ] Firewall: Only ports 80, 443 open
- [ ] Database backups (daily automated)
- [ ] CORS restricted to university domain
- [ ] Strong SECRET_KEY for JWT
- [ ] Regular security updates (OS + Docker images)

---

## 10. Key Decisions Log

### 10.1 Architecture Decisions

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2025-01-XX | **Use CSV storage initially** | Zero setup, pilot phase acceptable | SQLite (too early), PostgreSQL (overkill) |
| 2025-12-26 | **Migrate to SQLite (Phase 2)** | Data integrity required for production | PostgreSQL (too complex for handover) |
| 2025-12-26 | **Keep JavaScript (no TypeScript)** | Solo dev, learning curve too steep | TypeScript (rejected: 40+ hrs migration) |
| 2025-12-26 | **Migrate CRA → Vite** | CRA deprecated, Vite 10x faster builds | Next.js (overkill), stick with CRA (tech debt) |
| 2025-12-26 | **Docker for deployment** | University IT-friendly, cross-platform | Manual setup (error-prone), VMs (complex) |
| 2025-12-26 | **Critical path tests only** | Solo dev, focus on high-risk features | 80% coverage (too time-consuming) |
| 2025-12-26 | **Phased database migration** | Gradual risk reduction | Big bang migration (too risky) |

### 10.2 Feature Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-XX | **Bilingual (AR/EN) is mandatory** | University requirement, non-negotiable |
| 2025-01-XX | **No native mobile app** | Responsive web sufficient, 4 hrs/week constraint |
| 2025-12-26 | **Real-time updates deferred to Phase 4** | Pilot can use manual refresh, WebSockets low priority |
| 2025-12-26 | **No MFA/2FA** | Not required by university, adds complexity |
| 2025-12-26 | **Audit logging in Phase 3** | Important for compliance but not blocking pilot |

---

## 11. AI Assistant Instructions

### 11.1 How to Use This File

**When helping with this project:**

1. **ALWAYS read this file first** before making suggestions
2. **Respect the constraints** in Section 4 (solo dev, 4 hrs/week, JavaScript not TypeScript)
3. **Follow the roadmap** in Section 6 (don't suggest out-of-order features)
4. **Maintain bilingual support** - ALL user-facing text needs Arabic + English
5. **Keep it simple** - Prefer pragmatic solutions over "best practices" when time-constrained
6. **Update this file** when making architectural changes
7. **Refer to Gemini.md** for detailed feature history

### 11.2 Plan Mode & Plan Storage (CRITICAL)

**⚠️ IMPORTANT: Plans created in Plan Mode MUST be saved to persistent project locations**

**When creating implementation plans:**

1. **ALWAYS save plans to the project directory**, NOT to temporary Claude file-history folders
2. **Recommended location:** `.claude/` folder in the project root
3. **Naming convention:** Use descriptive names with dates
   - Good: `.claude/iau-theme-plan.md`, `.claude/database-migration-plan-2025-12.md`
   - Bad: `plan.md`, `temp-plan.md`

**Storage Rules:**
- ✅ **DO:** Save to `.claude/[descriptive-name].md` in project root
- ✅ **DO:** Include date in filename if multiple plans might exist
- ✅ **DO:** Use markdown format for readability
- ❌ **DON'T:** Rely on temporary file-history folders (they can be lost on crashes)
- ❌ **DON'T:** Save to user home directory (hard to find later)
- ❌ **DON'T:** Save outside the project directory

**Example Workflow:**
```markdown
User: "Create a plan for migrating to PostgreSQL"

Assistant Actions:
1. Creates detailed implementation plan
2. Saves to `.claude/postgresql-migration-plan-2025-12.md`
3. Confirms save location to user
4. References plan in CLAUDE.md if it's a major initiative
```

**Active Plans (Current):**
- **IAU Theme Adoption:** `.claude/iau-theme-plan.md` (Phase 3 in progress)
  - Phase 1: ✅ Foundation & Design System
  - Phase 2: ✅ Layout & Header Components
  - Phase 3: ⏳ Page Components (current)
  - Phase 4-6: 🔵 Planned

**Recovering Lost Plans:**
- Check `.claude/` folder first
- Check project root for `*plan*.md` files
- Check `~/.claude/file-history/[session-id]/` as last resort (may be incomplete)

### 11.3 Common Tasks & Quick Reference

**Adding a new API endpoint:**
1. Update `backend/models.py` (Pydantic model)
2. Update `backend/repositories.py` (data access)
3. Update `backend/services.py` (business logic)
4. Update `backend/main.py` (FastAPI endpoint)
5. Update `src/api.js` (frontend client)
6. Update translations.js (if user-facing)

**Adding a new page:**
1. Create `src/pages/NewPage.jsx`
2. Add route in `src/App.jsx`
3. Add sidebar link in `src/components/Sidebar.jsx`
4. Add to translations.js (AR + EN)
5. Update CLAUDE.md (this file)

**Database schema change:**
1. Update `backend/models.py`
2. Update `backend/repositories.py` (CSV column names)
3. Update CSV headers in `backend/data/*.csv`
4. Update `Gemini-database.md`
5. Write migration script (for SQLite later)

### 11.4 When to Ask vs. When to Proceed

**Always ask user before:**
- ❓ Changing tech stack (React → Vue, FastAPI → Flask, etc.)
- ❓ Adding new external dependencies
- ❓ Modifying database schema
- ❓ Changing authentication flow
- ❓ Removing existing features
- ❓ Deployment configuration changes

**You can proceed without asking:**
- ✅ Bug fixes
- ✅ UI/UX improvements (respecting bilingual requirement)
- ✅ Code refactoring (same functionality)
- ✅ Adding tests
- ✅ Documentation updates
- ✅ Performance optimizations

---

## 12. Quick Links & Resources

### 12.1 Documentation

- **This File (CLAUDE.md):** Comprehensive context for AI assistants
- **Gemini.md:** Detailed development history and feature log
- **Gemini-database.md:** Database schema reference
- **form-guide.md:** DOCX template placeholder guide

### 12.2 Key Technologies

- [React 19 Docs](https://react.dev)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Pydantic](https://docs.pydantic.dev)
- [Vite](https://vitejs.dev) ← Migration target
- [SQLAlchemy](https://www.sqlalchemy.org) ← Database ORM (Phase 2)

### 12.3 Development Commands

```bash
# Start backend (FastAPI)
python -m uvicorn backend.main:app --reload

# Start frontend (React)
npm start

# Run backend tests (once implemented)
pytest backend/

# Run frontend tests (once implemented)
npm test

# Build for production
npm run build

# Docker deployment (Phase 3)
docker-compose up -d
```

---

## 13. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1.0 | 2025-12-26 | Initial CLAUDE.md creation, tech stack validation, roadmap defined | Claude Sonnet 4.5 |
| 0.2.0 | 2025-12-27 | Vite migration complete, PostgreSQL migration complete | Claude Sonnet 4.5 |
| 0.3.0 | 2026-01-05 | **Security hardening complete**: JWT secrets, CORS restrictions, file upload validation, authorization checks, audit logging system, comprehensive security review | Claude Sonnet 4.5 |

---

## Appendix A: .gitignore Template

*See Section 8 Roadmap - will be created in Phase 1*

---

## Appendix B: Docker Configuration Template

*See Section 6.3 - will be created in Phase 3*

---

**END OF CLAUDE.md**

> **Next Steps:**
> 1. Initialize Git (Phase 1, Week 1)
> 2. Migrate CRA → Vite (Phase 2, Week 3)
> 3. Migrate CSV → SQLite (Phase 2, Week 4-5)
>
> **For University IT:** See Section 9 (Handover Strategy)
