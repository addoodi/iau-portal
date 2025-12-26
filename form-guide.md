# IAU Portal: Document Generation Guide

This guide explains how the backend generates `.docx` vacation forms and how to manage the template.

---

## 1. The "Template Approach"

The system uses the `docxtpl` Python library, which functions like a "mail merge" for Word documents.

-   **Template File:** A master `.docx` file is stored at `backend/templates/vacation_template.docx`. This file contains the complete design, layout, background image, and text formatting.
-   **Placeholders:** The template uses Jinja2-style placeholders (e.g., `{{ placeholder_name }}`) that are replaced with real data by the backend.
-   **Backend Logic:** When a user downloads a form, the backend performs the following steps:
    1.  Fetches the relevant leave request, employee, and manager data.
    2.  Performs necessary translations (e.g., "Annual" -> "سنوية").
    3.  Converts dates to the Hijri calendar format (`يوم/شهر/سنة هـ`).
    4.  Constructs a `context` data dictionary.
    5.  Renders the template, replacing the placeholders with the context data.
    6.  Streams the generated file to the user.

---

## 2. Placeholders

The following are the exact placeholders provided by the backend. Use these in the `vacation_template.docx` file.

| Placeholder | Description & Backend Value | Status |
| :--- | :--- | :--- |
| `{{ employee_name }}` | The employee's full name (e.g., "John Doe"). | ✅ Implemented |
| `{{ employee_id }}` | The employee's unique ID (e.g., "IAU-001"). | ✅ Implemented |
| `{{ manager_name }}` | The direct manager's full name. | ✅ Implemented |
| `{{ manager_position }}`| The manager's role (e.g., "manager"). **Note:** This currently uses the `role` from the `users` table, not the detailed Arabic position. | ✅ Improved (Uses Manager's Position) |
| `{{ vacation_type }}` | The vacation type, translated into Arabic (e.g., "سنوية"). | ✅ Implemented |
| `{{ start_date }}` | The request start date, converted to Hijri format. | ✅ Implemented |
| `{{ end_date }}` | The request end date, converted to Hijri format. | ✅ Implemented |
| `{{ duration }}` | The calculated duration of the leave in days. | ✅ Implemented |
| `{{ balance }}` | The employee's vacation balance. | ✅ Implemented (Uses live balance) |
| `{{ current_balance }}` | The employee's vacation balance at time of request. | ✅ Implemented |
| `{{ using_balance }}` | The amount of balance used for this request. Assumes it equals `duration`. | ✅ Implemented |
| `{{ approval_date }}` | The approval date in Hijri format. Empty if not approved. | ✅ Implemented |
| `{{ approval_x }}` | An "x" if the request status is "Approved". Empty otherwise. | ✅ Implemented |
| `{{ refusal_reason }}`| The reason for rejection. Empty if not rejected. | ✅ Implemented |

---

## 3. Action Items & Future Improvements

### 3.1. Implementing Signatures (Critical Instruction)

The backend logic for inserting signatures is **implemented**. However, for the signatures to appear correctly in the document layout, **you must modify the Word template manually**.

**Critical Step: Positioning Signatures**
The python-docx library cannot easily set "Behind Text" wrapping for inserted images programmatically. To ensure signatures appear in the correct spot without breaking the layout:

1.  **Open `backend/templates/vacation_template.docx` in Microsoft Word.**
2.  **Insert a Text Box (or Table Cell)** exactly where you want the signature to appear.
3.  **Remove the border/fill** of the Text Box/Table so it is invisible.
4.  **Insert the Placeholder Image** *inside* this Text Box/Table.
5.  **Set Alt Text:** Right-click the image -> **Format Picture** -> **Layout & Properties** -> **Alt Text**. Set the **Description** to `{{ employee_signature }}` (or `{{ manager_signature }}`).
6.  **Save** the template.

This acts as a container, fixing the position of the signature image on the page.

### 3.2. Data & Logic
-   **Vacation Balance:** The system now fetches the real `vacation_balance` and uses `{{ current_balance }}`.
-   **Manager Position:** The system now attempts to fetch the `position_ar` from the manager's employee record.