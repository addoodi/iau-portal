# IAU Portal: Project Overview & Development Guide

This document serves as the primary context and instruction manual for the IAU Portal project. It details the project's vision, architecture, current state, and critical development guidelines.

**Critical Instructions for Gemini CLI:**
1.  **Documentation Maintenance:** You MUST update this file (`GEMINI.md`) and any other relevant `.md` files (like `Gemini-database.md`, `form-guide.md`) whenever you make significant changes to the codebase, architecture, or data models. Keep the documentation synchronized with the code.
2.  **Localization:** ALL user-facing text MUST be localized. You must provide an Arabic translation for every English string added to the application. Use the `src/utils/translations.js` file for managing these strings and ensure the application respects the user's selected language (RTL/LTR).

---

## 1. Project Vision

The IAU Portal is a modern, secure web application designed to digitize and streamline employee administrative tasks at the Institute of Innovation and Entrepreneurship. Key features include leave management, attendance tracking, and hierarchical unit management.

---

## 2. Architecture Overview

The project is a full-stack application consisting of two main components:

### Frontend (React)
-   **Location:** `/src`
-   **Tech Stack:** React, Tailwind CSS, React Router DOM.
-   **State Management:** `PortalContext` (Context API) handles user session, data fetching, and localization state.
-   **Key Features:**
    -   Responsive UI with Sidebar and TopBar navigation.
    -   Role-based access control (Admin, Manager, Employee).
    -   Full English/Arabic localization with RTL support.
    -   Interactive dashboards and management forms.

### Backend (FastAPI)
-   **Location:** `/backend`
-   **Tech Stack:** Python, FastAPI, Pydantic, Pandas (for CSV persistence).
-   **Data Storage:** CSV files in `/backend/data` act as the persistence layer (Users, Employees, Units, Leave Requests).
-   **Key Features:**
    -   JWT-based authentication.
    -   RESTful API endpoints.
    -   Document generation (Docx templates).
    -   Business logic for vacation balance calculation and request processing.

### Documentation Map
-   **`GEMINI.md`**: (This file) The master guide and project status tracker. It provides a high-level overview and a detailed history of development.
-   **`Gemini-database.md`**: Defines the current data schema, models, and relationships as implemented in `backend/models.py` and persisted in the CSV files. Refer to this when modifying data structures.
-   **`form-guide.md`**: Instructions for modifying the `backend/templates/vacation_template.docx` file and understanding the available placeholders for document generation.

---

## 3. Implemented Features & Functionality

The following features have been successfully implemented and are currently functional:

### 3.1. Authentication & User Management
-   **Login & Session:** Secure login with JWT tokens. Automatic redirection to the dashboard upon successful login. User session is maintained across refreshes.
-   **First-Time Setup Flow:** If no users exist, the application redirects to a setup page to create the initial admin user, ensuring correct password hashing and data integrity.
-   **User Roles:** Implemented role-based access control (`admin`, `manager`, `employee`, `dean`) for UI elements and API endpoints.
-   **Add/Edit User:**
    -   Admins can create new users and modify existing employee profiles via a dedicated modal accessible from "User Management".
    -   Includes fields for English/Arabic names, job titles (`position_en`, `position_ar`), and unit assignment.
    -   **Manager Assignment:** Admins can select a "Direct Manager" for any employee from a dropdown list of eligible managers (users with 'manager', 'admin', or 'dean' roles).
    -   **Configurable Vacation Earn Rate:** Admins can now modify the `monthly_vacation_earned` rate (defaulting to 2.5 days/month) for individual employees.
-   **Profile Page:**
    -   Users can view their profile details (localized name, job title, unit).
    -   **Change Password:** Users can securely update their password.

### 3.2. Unit Management
-   **Unit Management Page:** Provides an overview of all organizational units.
-   **Hierarchy View:** Displays a hierarchical view by grouping employees under their respective units.
-   **Full CRUD Support:** Admins can now Add and Edit units via the UI, with data persisted to `units.csv` in the backend.

### 3.3. Leave Management
-   **Request Creation:** Employees can submit vacation requests (Annual, Sick, Emergency).
-   **"My Requests" Page:**
    -   Provides a table to track an employee's submitted requests, including localized Type, Dates, Status, and Actions.
    -   **Cancellation:** Employees can cancel their own requests if they are in "Pending" status.
    -   **Document Download:** For "Approved" requests, employees can download a pre-filled `.docx` vacation form.
-   **Approval Workflow:** Managers can view pending requests from their direct reports (or team) and Approve/Reject them. Status changes are persisted, and balances are updated upon approval.
-   **Vacation Balance:** The system automatically calculates the available vacation balance based on the employee's start date, monthly accrual rate, and approved leave requests.

### 3.4. Attendance Tracking (New)
-   **Dashboard Widget:** Employees can "Check In" and "Check Out" directly from the Dashboard.
-   **Real-time Status:** The widget displays the current status (Present/Absent/Completed) and timestamps.
-   **Backend Logging:** All attendance actions are recorded in `attendance_logs.csv` with timestamps and status.

### 3.5. Signature Management (New)
-   **Profile Upload:** Users can upload their digital signature (image) via the Profile page.
-   **Secure Storage:** Signatures are stored in `backend/data/signatures/` and linked to the employee profile.
-   **Document Integration:** Generated `.docx` vacation forms now automatically include the signatures of both the employee and their manager.

### 3.7. Admin Tools
-   **Delete User:** Admins can permanently delete users and their associated employee records from the "User Management" page.

### 3.8. Contract Management & Reporting
-   **Contract Logic:** Implemented 11-month auto-renewing contracts. Vacation balances are calculated based on the *current* contract period, and unused balances expire (reset) upon renewal.
-   **Expiration Warning:** The Dashboard displays a warning banner if the current contract has less than 40 days remaining.
-   **Dashboard Report:** Users can download a comprehensive `.docx` report of their current status (Profile, Balance, Attendance, Requests) directly from the Dashboard.

### 3.9. Enhanced Utilities
-   **Date System Toggle:** A global toggle in the TopBar allows switching all date displays between Gregorian and Hijri calendars.
-   **Email Infrastructure:** Basic email service architecture (`EmailService`) is in place (currently in mock mode) to support future notification features.

---

## 4. Technical Details & Recent Development History

This section details the significant architectural and code changes implemented during recent development.

### 4.1. Backend Enhancements
-   **Data Model (`backend/models.py`):**
    -   `EmployeeWithBalance` now includes `role` and `email` fields (derived from the associated `User` object).
    -   `Employee` model updated to include `position_en` (English job title).
    -   `EmployeeCreate` and `EmployeeUpdate` models now include `position_en` and `monthly_vacation_earned`.
    -   Introduced `EmployeeUpdate` and `UserPasswordUpdate` DTOs for update operations.
-   **Repositories (`backend/repositories.py`):**
    -   `CSVEmployeeRepository` updated to handle the new `position_en` column in `employees.csv`.
-   **Services (`backend/services.py`):**
    -   `EmployeeService._get_employee_with_balance` now populates `role` and `email` fields in `EmployeeWithBalance`.
    -   `UserService.initialize_first_user` updated to include `position_en` for the default admin.
    -   Implemented `UserService.change_password` for secure password updates.
    -   Implemented `EmployeeService.update_employee` for comprehensive employee profile modification, including user role updates.
-   **API Endpoints (`backend/main.py`):**
        -   Added `PUT /api/employees/{employee_id}` for updating employee profiles (admin-only).
        -   Added `POST /api/users/me/password` for changing user passwords.
        -   Added `POST /api/units` and `PUT /api/units/{id}` for Unit management.
        -   Added `POST /api/users/me/signature` for signature uploads.
        -   Added `POST /api/attendance/check-in`, `/check-out`, and `/today` for attendance tracking.
        -   Updated `PUT /api/requests/{id}` to enforce manager/admin role checks.
    
    ### 4.2. Frontend Refactoring & Bug Fixes
    -   **Unit Management:** Implemented `AddUnitModal` and connected it to the backend API.
    -   **Attendance:** Added "Today's Attendance" widget to `Dashboard.jsx` with real-time check-in/out functionality.
    -   **Approvals:** Refactored `Approvals.jsx` to correctly filter team requests based on `manager_id` and use proper data fields.
    -   **Signatures:** Connected `Profile.jsx` signature upload to the backend.
    -   **UI/Aesthetic Regression Fix:** Re-implemented `Sidebar.jsx` and `TopBar.jsx` in `src/components` from `Example files/old website` to restore intended visual style and applied modern `react-router-dom` navigation.
    -   **Consolidated Components:** Removed inline `Sidebar` and `TopBar` definitions from `src/App.jsx`.
    -   **Frontend Compilation Errors:** Resolved `SyntaxError` from duplicate `App` component definition and missing `MainLayout` closing brace in `src/App.jsx`.
    -   **Script Execution Robustness:** Provided guidance for resolving PowerShell execution policy issues when running the frontend development server.
    -   **Admin User Setup:** Fixed initial admin login failure by ensuring `users.csv` and `employees.csv` are properly synchronized to trigger the first-time setup flow.
    -   **Dashboard `NaN` Errors:** Addressed `NaN` display issues and `undefined.charAt` crashes in `src/pages/Dashboard.jsx` by:
        -   Ensuring `user` object in `PortalContext` contains `role`, `email`, `name_ar`, `name_en`.
        -   Switching from `users` to `employees` data in `Dashboard`'s `teamMembers` logic.
        -   Implementing robust optional chaining and fallbacks for UI elements accessing potentially incomplete data.
    -   **"Not Authorized" Error for Non-Admins:** Fixed by making `fetchUsers()` call in `PortalContext` conditional based on `user.role` to prevent unauthorized access to `GET /api/users`.
    -   **Infinite Dashboard Refresh Loop:** Resolved by refining `PortalContext`'s `refreshData` dependency array (`[user?.user_id, user?.role]`) to prevent unnecessary re-executions.
    -   **Login Redirection:** Implemented `useEffect` and `useNavigate` in `src/pages/LoginPage.jsx` to ensure automatic redirection to the dashboard after successful login.
    -   **Localization Consistency:** Standardized name and position display across `Sidebar`, `TopBar`, `Dashboard`, and `Profile` using `lang` to toggle between `_ar` and `_en` fields.
    -   **`RequestModal` Fix:** Recreated the deleted `src/components/RequestModal.jsx` (which was accidentally removed due to misinterpretation of obsolete files).
        - **Linting Cleanup:** Removed unused `Link` and `useEffect` imports from `src/App.jsx` and `src/components/AddUserModal.jsx` respectively.
    
    ### 4.3. Feature Completion: Add User & Employee Management
    -   **Backend Implementation:**
        -   **Model:** Added `EmployeeCreate` Pydantic model to `backend/models.py` to validate input for atomic user and employee creation.
        -   **Service:** Implemented `create_user_and_employee` in `EmployeeService` (`backend/services.py`) to handle `User` creation (auth) and `Employee` profile creation (business data) in a single flow.
        -   **API:** Added `POST /api/employees` endpoint in `backend/main.py`, protected by admin role check.
    -   **Frontend Implementation:**
        -   **API Layer:** Updated `src/api.js` to include `createEmployee` and `updateEmployee` functions.
        -   **Component:** Created `src/components/AddUserModal.jsx` featuring:
            -   Comprehensive form with fields for User (email, password, role) and Employee (localized names/positions, unit, manager, start date).
            -   Dynamic fetching of Units and Managers for dropdown selections.
            -   Form validation and error handling.
        -   **Integration:** Updated `src/pages/UserManagement.jsx` to utilize `AddUserModal` for both creating new users and editing existing ones.
        -   **Context:** Verified `PortalContext.jsx` correctly processes and merges employee data (including localized name generation) for seamless UI rendering.

    ### 4.4. Feature Completion: Mailing, Attachments, & Refinements
    -   **Mailing System Configuration:**
        -   **Backend:** Implemented `EmailSettings` model, `CSVEmailSettingsRepository`, and `EmailSettingsService` (with secure password hashing and SMTP testing). Added secure API endpoints for configuration.
        -   **Frontend:** Created `SiteSettings.jsx` for admins to configure and test SMTP settings.
    -   **Attachments:**
        -   **Backend:** Updated `LeaveRequest` model to support a list of file paths. Added `upload_attachment` and `download_attachment` endpoints in `main.py` and file saving logic in `services.py`.
        -   **Frontend:** Updated `RequestModal.jsx` to support file selection. Updated `MyRequests.jsx` and `Approvals.jsx` to display attachment links (paperclip icon) for users and managers.
    -   **Rejection Reason:**
        -   **Frontend:** Implemented a mandatory reason input in `Approvals.jsx` when rejecting a request. Updated `MyRequests.jsx` to display this reason to the employee.
    -   **Critical Bug Fixes:**
        -   **ID Collision:** Fixed `create_user_and_employee` in `services.py` to use `max(id) + 1` instead of `count + 1`, preventing overwrites when IDs are non-sequential.
        -   **Data Repair:** Manually corrected `users.csv` and `employees.csv` to restore overwritten user data (Raghad) and assign a new ID to the conflicting user (Abdullah).
        -   **Localization:** Added missing translations for Dashboard, Profile, Approvals, and Site Settings pages.

    ---
    
    ## 5. Current Status
    
    The application is stable, feature-complete, and includes all requested administrative and user-facing functionality.
    
    -   **Frontend:** Running on `http://localhost:3000` (Use `npm start`).
    -   **Backend:** Running on `http://127.0.0.1:8000` (Use `python -m uvicorn backend.main:app --reload`).
    
    **Pending Tasks / Known Limitations:**
    -   **Production Deployment:** Containerization (Docker) and migration to a robust database (e.g., PostgreSQL) are planned for production hardening.
    -   **Advanced Reporting:** While attendance is tracked, admin reports for attendance history are not yet implemented in the UI.

    **Completed Action Items (Last Sprint):**
    1.  **Document Generation:**
        -   **Signature Positioning:** *[Action Required by User]* The `.docx` template must be modified manually. Place the `{{ employee_signature_path }}` and `{{ manager_signature_path }}` placeholders inside a **Text Box** or **Table Cell** with fixed dimensions.
        -   **Vacation Balance:** [Completed] Added `{{ current_balance }}` placeholder.
        -   **Vacation Type:** [Completed] Localized types (including "Emergency").
        -   **Rejection Handling:** [Completed] Verified logic for rejected forms.
    2.  **Dashboard & Reporting:**
        -   **Manager Report:** [Completed] Added "Team Overview" to reports.
        -   **Role Localization:** [Completed] Dynamic localized role names implemented.
        -   **Conflict Detection:** [Completed] Implemented overlap warnings in `Approvals.jsx`.
    3.  **Localization Gaps:** [Completed] All identified gaps filled.
    4.  **Feature Requests:**
        -   **Attachments:** [Completed] Full upload/download/view flow implemented.
        -   **Rejection Reason:** [Completed] Mandatory input implemented.
        -   **Mailing System:** [Completed] Full configuration and testing UI implemented.
    5.  **Bug Investigation:**
        -   **Ghost User/Collision:** [Completed] Resolved ID generation bug and repaired data.

    **How to Run:**
    1.  **Backend:** `python -m uvicorn backend.main:app --reload`
    2.  **Frontend:** `npm start`
    3.  **Mailing:** Go to `/site-settings` (Admin only) to configure SMTP.
    4.  **Template:** Ensure `vacation_template.docx` is updated with text boxes for signatures as per instructions.

    **Status Update (Latest):**
    All requested features from the "User Feedback & Action Items" list have been implemented and verified via static analysis and diagnostic scripts.
    -   **Network Access:** Configured for **universal** local network access. The backend now accepts requests from ANY origin (CORS: `*`), and the frontend adapts to the hostname.
    -   **Document Generation:** Fixed (User must update template).
    -   **Dashboard:** Team overview added.
    -   **Localization:** Gaps filled.
    -   **Attachments:** Implemented (Backend & Frontend).
    -   **Rejection Reason:** Implemented.
    -   **Mailing System:** Implemented (Backend & Frontend).
    -   **Backend:** Verified import integrity.

    **How to Run:**
    1.  **Backend:** `python -m uvicorn backend.main:app --reload`
    2.  **Frontend:** `npm start`
    3.  **Mailing:** Go to `/site-settings` (Admin only) to configure SMTP.
    4.  **Template:** Ensure `vacation_template.docx` is updated with text boxes for signatures as per instructions.
    