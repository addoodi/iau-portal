import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
import os

from .models import User, Employee, LeaveRequest, Unit, AttendanceLog, EmailSettings

class BaseRepository(ABC):
    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, id):
        pass

    @abstractmethod
    def add(self, entity):
        pass

    @abstractmethod
    def update(self, entity):
        pass

    @abstractmethod
    def delete(self, id):
        pass

class CSVUserRepository(BaseRepository):
    def __init__(self, file_path='backend/data/users.csv'):
        self.file_path = file_path
        self.df = self._load_df()

    def _load_df(self):
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            return pd.read_csv(self.file_path)
        return pd.DataFrame(columns=['id', 'email', 'password_hash', 'role', 'is_active'])

    def _save_df(self):
        self.df.to_csv(self.file_path, index=False)

    def get_all(self) -> List[User]:
        return [User(**row) for index, row in self.df.iterrows()]

    def get_by_id(self, id: UUID) -> Optional[User]:
        user_row = self.df[self.df['id'] == str(id)]
        if not user_row.empty:
            return User(**user_row.iloc[0].to_dict())
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        user_row = self.df[self.df['email'] == email]
        if not user_row.empty:
            return User(**user_row.iloc[0].to_dict())
        return None

    def add(self, user: User) -> User:
        new_row = pd.DataFrame([user.dict()])
        new_row['id'] = new_row['id'].astype(str)

        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return user

    def update(self, user: User) -> User:
        self.df = self.df[self.df['id'] != str(user.id)]
        new_row = pd.DataFrame([user.dict()])
        new_row['id'] = new_row['id'].astype(str)
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return user

    def delete(self, id: UUID):
        self.df = self.df[self.df['id'] != str(id)]
        self._save_df()

class CSVEmailSettingsRepository(BaseRepository):
    def __init__(self, file_path='backend/data/email_settings.csv'):
        self.file_path = file_path
        self.df = self._load_df()

    def _load_df(self):
        # Email settings will have only one row with ID 1
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            df = pd.read_csv(self.file_path)
            # Ensure it's not empty and has the correct ID
            if not df.empty and df['id'].iloc[0] == 1:
                return df
        return pd.DataFrame(columns=['id', 'smtp_host', 'smtp_port', 'smtp_username', 'smtp_password_hash', 'sender_email', 'is_active'])

    def _save_df(self):
        self.df.to_csv(self.file_path, index=False)

    def get_all(self) -> List[EmailSettings]:
        df_filled = self.df.astype(object).where(pd.notna(self.df), None)
        return [EmailSettings(**row) for index, row in df_filled.iterrows()]

    def get_by_id(self, id: int) -> Optional[EmailSettings]:
        if id != 1: # Only ID 1 is supported for email settings
            return None
        if not self.df.empty and self.df['id'].iloc[0] == 1:
            row_dict = self.df.iloc[0].to_dict()
            for key, value in row_dict.items():
                if pd.isna(value):
                    row_dict[key] = None
            return EmailSettings(**row_dict)
        return None

    def add(self, settings: EmailSettings) -> EmailSettings:
        if not self.df.empty: # Settings already exist
            raise Exception("Email settings already configured. Use update instead.")
        
        new_row = pd.DataFrame([settings.dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return settings

    def update(self, settings: EmailSettings) -> EmailSettings:
        if self.df.empty: # No settings to update
            raise Exception("Email settings not configured. Use add instead.")
        
        # Replace the single row
        self.df = pd.DataFrame([settings.dict()])
        self._save_df()
        return settings
    
    def delete(self, id: int):
        if id != 1:
            return
        self.df = pd.DataFrame(columns=['id', 'smtp_host', 'smtp_port', 'smtp_username', 'smtp_password_hash', 'sender_email', 'is_active'])
        self._save_df()

class CSVEmployeeRepository(BaseRepository):
    def __init__(self, file_path='backend/data/employees.csv'):
        self.file_path = file_path
        self.df = self._load_df()

    def _load_df(self):
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            df = pd.read_csv(self.file_path)

            # Auto-migration: Add contract_auto_renewed column if missing
            if 'contract_auto_renewed' not in df.columns:
                df['contract_auto_renewed'] = False
                # Save the updated CSV with the new column
                df.to_csv(self.file_path, index=False)
                print("Migration: Added 'contract_auto_renewed' column to employees.csv")

            return df
        return pd.DataFrame(columns=['id', 'user_id', 'first_name_ar', 'last_name_ar', 'first_name_en', 'last_name_en', 'position_ar', 'position_en', 'unit_id', 'manager_id', 'start_date', 'monthly_vacation_earned', 'signature_path', 'contract_auto_renewed'])

    def _save_df(self):
        self.df.to_csv(self.file_path, index=False)

    def get_all(self) -> List[Employee]:
        df_filled = self.df.astype(object).where(pd.notna(self.df), None)
        return [Employee(**row) for index, row in df_filled.iterrows()]

    def get_by_id(self, id: str) -> Optional[Employee]:
        employee_row = self.df[self.df['id'] == id]
        if not employee_row.empty:
            row_dict = employee_row.iloc[0].to_dict()
            # Replace NaN with None for Pydantic model
            for key, value in row_dict.items():
                if pd.isna(value):
                    row_dict[key] = None
            return Employee(**row_dict)
        return None

    def get_by_user_id(self, user_id: UUID) -> Optional[Employee]:
        employee_row = self.df[self.df['user_id'] == str(user_id)]
        if not employee_row.empty:
            row_dict = employee_row.iloc[0].to_dict()
            for key, value in row_dict.items():
                if pd.isna(value):
                    row_dict[key] = None
            return Employee(**row_dict)
        return None

    def add(self, employee: Employee):
        new_row = pd.DataFrame([employee.dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return employee

    def update(self, employee: Employee):
        self.df = self.df[self.df['id'] != employee.id]
        new_row = pd.DataFrame([employee.dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return employee

    def delete(self, id: str):
        self.df = self.df[self.df['id'] != id]
        self._save_df()

class CSVLeaveRequestRepository(BaseRepository):
    def __init__(self, file_path='backend/data/leave_requests.csv'):
        self.file_path = file_path
        self.df = self._load_df()

    def _load_df(self):
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            df = pd.read_csv(self.file_path)
            # Convert 'attachments' column from string to list
            if 'attachments' in df.columns:
                df['attachments'] = df['attachments'].apply(lambda x: eval(x) if pd.notna(x) else [])
            return df
        return pd.DataFrame(columns=['id', 'employee_id', 'vacation_type', 'start_date', 'end_date', 'duration', 'status', 'rejection_reason', 'approval_date', 'balance_used', 'attachments'])

    def _save_df(self):
        # Convert 'attachments' list to string before saving
        df_to_save = self.df.copy()
        if 'attachments' in df_to_save.columns:
            df_to_save['attachments'] = df_to_save['attachments'].apply(str)
        df_to_save.to_csv(self.file_path, index=False)

    def get_all(self) -> List[LeaveRequest]:
        df_filled = self.df.astype(object).where(pd.notna(self.df), None)
        return [LeaveRequest(**row) for index, row in df_filled.iterrows()]

    def get_by_id(self, id: int) -> Optional[LeaveRequest]:
        self.df['id'] = self.df['id'].astype(int)
        leave_request_row = self.df[self.df['id'] == id]
        if not leave_request_row.empty:
            row_dict = leave_request_row.iloc[0].to_dict()
            # Manually handle NaN values, skipping list/array columns
            for key, value in row_dict.items():
                if isinstance(value, (list, np.ndarray)):
                    # Keep list values as-is
                    continue
                try:
                    if pd.isna(value):
                        row_dict[key] = None
                except (ValueError, TypeError):
                    # If pd.isna fails, keep the value as-is
                    pass
            return LeaveRequest(**row_dict)
        return None
    
    def add(self, leave_request: LeaveRequest) -> LeaveRequest:
        new_row = pd.DataFrame([leave_request.dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return leave_request

    def update(self, leave_request: LeaveRequest) -> LeaveRequest:
        self.df['id'] = self.df['id'].astype(int)
        self.df = self.df[self.df['id'] != leave_request.id]
        new_row = pd.DataFrame([leave_request.dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return leave_request
    
    def delete(self, id: int):
        self.df['id'] = self.df['id'].astype(int)
        self.df = self.df[self.df['id'] != id]
        self._save_df()

class CSVUnitRepository(BaseRepository):
    def __init__(self, file_path='backend/data/units.csv'):
        self.file_path = file_path
        self.df = self._load_df()

    def _load_df(self):
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            return pd.read_csv(self.file_path)
        return pd.DataFrame(columns=['id', 'name_en', 'name_ar'])

    def _save_df(self):
        self.df.to_csv(self.file_path, index=False)

    def get_all(self) -> List[Unit]:
        df_filled = self.df.astype(object).where(pd.notna(self.df), None)
        return [Unit(**row) for index, row in df_filled.iterrows()]

    def get_by_id(self, id: int) -> Optional[Unit]:
        self.df['id'] = self.df['id'].astype(int)
        unit_row = self.df[self.df['id'] == id]
        if not unit_row.empty:
            row_dict = unit_row.iloc[0].to_dict()
            for key, value in row_dict.items():
                if pd.isna(value):
                    row_dict[key] = None
            return Unit(**row_dict)
        return None
    
    def add(self, unit: Unit) -> Unit:
        new_row = pd.DataFrame([unit.dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return unit

    def update(self, unit: Unit) -> Unit:
        self.df['id'] = self.df['id'].astype(int)
        self.df = self.df[self.df['id'] != unit.id]
        new_row = pd.DataFrame([unit.dict()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return unit
    
    def delete(self, id: int):
        self.df['id'] = self.df['id'].astype(int)
        self.df = self.df[self.df['id'] != id]
        self._save_df()

class CSVAttendanceRepository(BaseRepository):
    def __init__(self, file_path='backend/data/attendance_logs.csv'):
        self.file_path = file_path
        self.df = self._load_df()

    def _load_df(self):
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            return pd.read_csv(self.file_path)
        return pd.DataFrame(columns=['id', 'employee_id', 'date', 'check_in', 'check_out', 'status'])

    def _save_df(self):
        self.df.to_csv(self.file_path, index=False)

    def get_all(self) -> List[AttendanceLog]:
        df_filled = self.df.astype(object).where(pd.notna(self.df), None)
        return [AttendanceLog(**row) for index, row in df_filled.iterrows()]

    def get_by_id(self, id: UUID) -> Optional[AttendanceLog]:
        log_row = self.df[self.df['id'] == str(id)]
        if not log_row.empty:
            row_dict = log_row.iloc[0].to_dict()
            for key, value in row_dict.items():
                if pd.isna(value):
                    row_dict[key] = None
            return AttendanceLog(**row_dict)
        return None
    
    def get_by_employee_and_date(self, employee_id: str, date: str) -> Optional[AttendanceLog]:
        log_row = self.df[(self.df['employee_id'] == employee_id) & (self.df['date'] == date)]
        if not log_row.empty:
            row_dict = log_row.iloc[0].to_dict()
            for key, value in row_dict.items():
                if pd.isna(value):
                    row_dict[key] = None
            return AttendanceLog(**row_dict)
        return None

    def add(self, log: AttendanceLog) -> AttendanceLog:
        new_row = pd.DataFrame([log.dict()])
        new_row['id'] = new_row['id'].astype(str)
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return log

    def update(self, log: AttendanceLog) -> AttendanceLog:
        self.df = self.df[self.df['id'] != str(log.id)]
        new_row = pd.DataFrame([log.dict()])
        new_row['id'] = new_row['id'].astype(str)
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_df()
        return log

    def delete(self, id: UUID):
        self.df = self.df[self.df['id'] != str(id)]
        self._save_df()