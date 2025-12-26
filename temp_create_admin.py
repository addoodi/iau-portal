
import pandas as pd
from backend.auth import get_password_hash
import uuid
import os

# --- Configuration ---
EMAIL = "admin@iau.com"
PASSWORD = "password"
ROLE = "admin"
IS_ACTIVE = True
USERS_FILE_PATH = os.path.join('backend', 'data', 'users.csv')
EMPLOYEES_FILE_PATH = os.path.join('backend', 'data', 'employees.csv')

# --- Generate User ---
user_id = str(uuid.uuid4())
hashed_password = get_password_hash(PASSWORD)

# --- Create DataFrames ---
new_user_df = pd.DataFrame([{
    "id": user_id,
    "email": EMAIL,
    "password": hashed_password,
    "role": ROLE
}])

new_employee_df = pd.DataFrame([{
    "id": "1", # Simple ID for the first employee
    "user_id": user_id,
    "first_name_ar": "مدير",
    "last_name_ar": "النظام",
    "position_ar": "مسؤول النظام",
    "department_ar": "تقنية المعلومات",
    "manager_id": None,
    "vacation_balance": 30,
    "signature_path": None
}])


# --- Update Users CSV ---
try:
    users_df = pd.read_csv(USERS_FILE_PATH)
    if EMAIL not in users_df['email'].values:
        users_df = pd.concat([users_df, new_user_df], ignore_index=True)
        users_df.to_csv(USERS_FILE_PATH, index=False)
        print(f"User '{EMAIL}' created in {USERS_FILE_PATH}.")
    else:
        print(f"User '{EMAIL}' already exists in {USERS_FILE_PATH}.")
except (FileNotFoundError, pd.errors.EmptyDataError):
    new_user_df.to_csv(USERS_FILE_PATH, index=False)
    print(f"Created {USERS_FILE_PATH} and added user '{EMAIL}'.")


# --- Update Employees CSV ---
try:
    employees_df = pd.read_csv(EMPLOYEES_FILE_PATH)
    if user_id not in employees_df['user_id'].values:
        employees_df = pd.concat([employees_df, new_employee_df], ignore_index=True)
        employees_df.to_csv(EMPLOYEES_FILE_PATH, index=False)
        print(f"Associated employee record created in {EMPLOYEES_FILE_PATH}.")
    else:
        print(f"Employee for user_id '{user_id}' already exists in {EMPLOYEES_FILE_PATH}.")
except (FileNotFoundError, pd.errors.EmptyDataError):
    new_employee_df.to_csv(EMPLOYEES_FILE_PATH, index=False)
    print(f"Created {EMPLOYEES_FILE_PATH} and added associated employee.")

