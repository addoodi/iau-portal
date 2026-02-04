# IAU Portal - Manual QA Checklist

**Version:** 0.4.0 | **Estimated Time:** ~20 minutes

Run this checklist after each deployment to verify the application is working correctly.

---

## Prerequisites

- Application running (all containers healthy or backend + frontend started manually)
- At least one admin account initialized
- At least one manager and one employee account created

---

## 0. Infrastructure

- [ ] Backend health check returns OK
  ```
  GET /api/health -> {"status": "healthy"}
  ```
- [ ] Frontend loads the login page without errors
- [ ] Browser console shows no critical errors (F12 > Console)

---

## 1. Authentication

- [ ] **Login (valid credentials)** -> redirects to dashboard
- [ ] **Login (wrong password)** -> error message displayed, not logged in
- [ ] **Login (non-existent email)** -> error message displayed
- [ ] **Access protected page without login** -> redirected to login
- [ ] **Logout** -> redirected to login, protected pages inaccessible
- [ ] **Language toggle** on login page works (AR/EN)

---

## 2. Employee - Leave Request Flow

Login as an **employee** account:

- [ ] Dashboard shows vacation balance (Total, Used, Available)
- [ ] **Create new leave request:**
  - [ ] Select vacation type (Annual, Sick, etc.)
  - [ ] Select start and end dates
  - [ ] Duration is auto-calculated
  - [ ] Submit succeeds, status shows "Pending"
- [ ] Request appears in **My Requests** list
- [ ] **File attachment:** attach a PDF file (<10MB) -> accepted
- [ ] **File validation:** attempt to attach a .exe file -> rejected with error

---

## 3. Manager - Approval Flow

Login as a **manager** account:

- [ ] Pending request visible in **Approvals** page
- [ ] **Approve** a request:
  - [ ] Status changes to "Approved"
  - [ ] Approval date is set
  - [ ] Employee balance is updated (deducted)
- [ ] **Reject** a different request:
  - [ ] Rejection reason field required
  - [ ] Status changes to "Rejected"
  - [ ] Employee balance is NOT deducted

---

## 4. Document Generation

- [ ] Download vacation form (DOCX) for an approved request
- [ ] Document opens correctly in Word/LibreOffice
- [ ] Contains correct employee name (Arabic + English)
- [ ] Contains correct dates (Hijri + Gregorian)
- [ ] Contains correct vacation type and duration

---

## 5. Admin Functions

Login as an **admin** account:

- [ ] **View employee list** -> all employees displayed
- [ ] **Add new employee** -> fills form, employee created and appears in list
- [ ] **Edit employee** -> changes saved correctly
- [ ] **View audit logs** (`/api/admin/audit-logs`) -> shows recent actions
  - [ ] Login events appear
  - [ ] Approval/rejection events appear
  - [ ] Employee creation events appear
- [ ] **Manage units** -> add, edit, and delete organizational units

---

## 6. Bilingual Support

- [ ] Switch to **Arabic** -> all UI text in Arabic, RTL layout
- [ ] Switch to **English** -> all UI text in English, LTR layout
- [ ] Leave request form works correctly in both languages
- [ ] Dashboard data (names, dates) renders in selected language
- [ ] Navigation items translated correctly

---

## 7. Mobile Responsiveness

Open on a mobile device or browser DevTools (toggle device toolbar):

- [ ] Login page usable and readable
- [ ] Dashboard layout adapts to narrow screen
- [ ] Navigation is accessible (sidebar/hamburger menu)
- [ ] Forms are usable (inputs reachable, buttons tappable)

---

## 8. Security Spot Checks

- [ ] **Unauthorized access:** Employee cannot access other employees' documents
- [ ] **Role enforcement:** Non-admin cannot access `/api/admin/audit-logs` (returns 403)
- [ ] **Non-manager rejection:** Regular employee cannot approve another employee's request (returns 403)

---

## Results

| Field | Value |
|-------|-------|
| **Date** | |
| **Tester** | |
| **Environment** | [ ] Local Docker  [ ] Staging  [ ] Production |
| **All tests passed** | [ ] Yes  [ ] No |
| **Issues found** | |
| **Notes** | |
