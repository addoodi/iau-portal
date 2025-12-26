# IAU Portal: Database & Data Schema

## 1. Current Development State

-   **Backend:** A functional FastAPI application that serves APIs and can generate `.docx` files. It uses **CSV files** located in `backend/data/` as the persistence layer.
-   **Frontend:** A high-fidelity React application fully connected to the backend API. All data (Users, Employees, Requests, Units, Attendance) is fetched and mutated via the API.
-   **The Goal:** The next phase is to migrate from CSV files to a production-ready SQL database (e.g., PostgreSQL). The schemas below define the target structure.

---

## 2. Target Data Schemas

These schemas are implemented in the backend's Pydantic models (`backend/models.py`) and reflected in the CSV files.

### 2.1. `users`
Stores login credentials and permissions.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key. |
| `email` | String (Email) | The user's unique login email. |
| `password_hash`| String | Hashed password (using bcrypt). NEVER store plain text. |
| `role` | String | User's role (`admin`, `manager`, `employee`). |
| `is_active` | Boolean | Whether the user can log in. |

### 2.2. `employees`
Stores detailed information for every employee. This is the central source of truth for user profiles and document generation.

*Note on Contracts:* The system assumes an 11-month auto-renewing contract cycle starting from `start_date`. Vacation balances are calculated dynamically for the *current* cycle.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | String | Primary Key (e.g., "IAU-001"). |
| `user_id` | UUID | Foreign Key to `users.id`. Links an employee profile to a login. |
| `first_name_ar` | String | First name in Arabic. |
- `last_name_ar` (VARCHAR): Last Name in Arabic
- `first_name_en` (VARCHAR): First Name in English
- `last_name_en` (VARCHAR): Last Name in English
- `position_ar` (VARCHAR): Job Title in Arabic
- `position_en` (VARCHAR): Job Title in English
- `unit_id` (INTEGER): Foreign Key to Units table
- `manager_id` (VARCHAR): Self-referencing FK to Employees table (Direct Manager)
| `vacation_balance`| Integer | Current number of available vacation days. |
| `signature_path` | String | *Nullable*. File path to a transparent signature image (e.g., `backend/data/signatures/IAU-001_signature.png`). |

### 2.3. `leave_requests`
Stores all information related to an employee's request for leave.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Primary Key. |
| `employee_id` | String | Foreign Key to `employees.id`. |
| `vacation_type` | String | Type of leave (e.g., 'Annual', 'Sick'). Stored in English, translated on generation. |
| `start_date` | String | Format: `YYYY-MM-DD`. |
| `end_date` | String | Format: `YYYY-MM-DD`. |
| `duration` | Integer | Total number of days requested. |
| `status` | String | `Pending`, `Approved`, `Rejected`. |
| `rejection_reason` | String | *Nullable*. Reason provided if the request is rejected. |
| `approval_date` | String | *Nullable*. Date of approval in `YYYY-MM-DD` format. |
| `balance_used` | Integer | The number of days deducted from `vacation_balance` for this request. |
| `attachments` | List[String] | List of file paths for uploaded documents (e.g., sick leave notes). |

### 2.4. `attendance_logs`
Stores daily attendance records.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key. |
| `employee_id` | String | Foreign Key to `employees.id`. |
| `date` | String | `YYYY-MM-DD`. |
| `check_in` | Datetime | Timestamp of check-in. |
| `check_out` | Datetime | *Nullable*. Timestamp of check-out. |
| `status` | String | `Present`, `Absent`, `Late`. |

### 2.5. `units`
Stores organizational units (departments).

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Primary Key. |
| `name_en` | String | Unit name in English. |
| `name_ar` | String | Unit name in Arabic. |

### 2.6. `email_settings`
Stores configuration for the SMTP mailing service. (Single row).

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Primary Key (Always 1). |
| `smtp_host` | String | SMTP Server Hostname. |
| `smtp_port` | Integer | SMTP Server Port. |
| `smtp_username` | String | SMTP Username. |
| `smtp_password_hash` | String | Hashed SMTP Password. |
| `sender_email` | String | The "From" email address. |
| `is_active` | Boolean | Global toggle for the email service. |

---

## 3. Action Items & Development Roadmap

### Completed Phases
-   **Phase 1: Backend Schema Alignment:** Models and Repositories are fully aligned with CSV persistence.
-   **Phase 2: Frontend-Backend Integration:** All core features (Auth, Units, Requests, Attendance) are integrated.

### Phase 3: Data & Infrastructure Hardening
*Goal: Move from a prototype to a robust application.*

1.  **Create Admin Tools:** Develop a secure section in the frontend for `admin` users to manage employees, users, departments, and positions. (Partially done with Add User/Unit modals).
2.  **Database Migration:** Plan and execute the migration from CSV files to a proper database (e.g., SQLite for ease of development, PostgreSQL for production). This involves implementing the `PostgresRepository` classes.
3.  **Containerization:** Dockerize the application for easier deployment.