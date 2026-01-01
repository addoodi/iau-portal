import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
import os

from .models import User, Employee, LeaveRequest, Unit, AttendanceLog, EmailSettings


# Migration Helper - Ensures CSV schema compatibility
def migrate_csv_schema(df: pd.DataFrame, expected_schema: Dict[str, Any], csv_name: str) -> pd.DataFrame:
    """
    Automatically migrates CSV files to match expected schema.

    Args:
        df: DataFrame to migrate
        expected_schema: Dict of {column_name: default_value}
        csv_name: Name of CSV for logging

    Returns:
        Migrated DataFrame with all expected columns
    """
    migrations_applied = []

    for column, default_value in expected_schema.items():
        if column not in df.columns:
            df[column] = default_value
            migrations_applied.append(f"  + Added '{column}' column with default: {default_value}")

    if migrations_applied:
        print(f"\n📋 Schema Migration for {csv_name}:")
        for migration in migrations_applied:
            print(migration)
        print(f"✅ Migration completed successfully\n")

    return df


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
        # Define expected schema with default values
        expected_schema = {
            'id': None,
            'email': None,
            'password_hash': None,
            'role': 'employee',
            'is_active': True
        }

        if os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)

            # If file has content, try to read it
            if file_size > 100:  # More than just a header line
                try:
                    # Force UTF-8 encoding and treat id as string
                    df = pd.read_csv(self.file_path, encoding='utf-8', dtype={'id': str})
                    # Apply automatic migration
                    df = migrate_csv_schema(df, expected_schema, 'users.csv')
                    # Save migrated schema
                    df.to_csv(self.file_path, index=False)
                    return df
                except pd.errors.EmptyDataError:
                    # File appears empty to pandas - might be locked or corrupted
                    print(f"WARNING: {self.file_path} has {file_size} bytes but pandas sees no data.")
                    print(f"This might be a file lock issue. Retrying...")
                    import time
                    time.sleep(0.1)  # Wait 100ms for file lock to release
                    try:
                        df = pd.read_csv(self.file_path, encoding='utf-8', dtype={'id': str})
                        df = migrate_csv_schema(df, expected_schema, 'users.csv')
                        df.to_csv(self.file_path, index=False)
                        return df
                    except Exception as retry_error:
                        print(f"RETRY FAILED: {retry_error}")
                        # Fall through to create empty schema
                        df = pd.DataFrame(columns=list(expected_schema.keys()))
                        return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

            # File is very small (just headers or empty) - only recreate if truly empty
            elif file_size == 0:
                print(f"Info: {self.file_path} is completely empty (0 bytes). Creating with schema.")
                df = pd.DataFrame(columns=list(expected_schema.keys()))
                df.to_csv(self.file_path, index=False)
                return df
            else:
                # File has some content (likely just headers) - try to read
                try:
                    # Force UTF-8 encoding and treat id as string
                    df = pd.read_csv(self.file_path, encoding='utf-8', dtype={'id': str})
                    df = migrate_csv_schema(df, expected_schema, 'users.csv')
                    df.to_csv(self.file_path, index=False)
                    return df
                except pd.errors.EmptyDataError:
                    # File has headers but no data rows - that's OK
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    df.to_csv(self.file_path, index=False)
                    return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

        # File doesn't exist - create new
        print(f"Info: {self.file_path} does not exist. Creating new file.")
        df = pd.DataFrame(columns=list(expected_schema.keys()))
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        df.to_csv(self.file_path, index=False)
        return df

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
        # Define expected schema with default values
        expected_schema = {
            'id': 1,
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_username': None,
            'smtp_password_hash': None,
            'sender_email': None,
            'is_active': False
        }

        if os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)

            # If file has content (more than just headers), try to read it
            if file_size > 100:  # More than just a header line
                try:
                    df = pd.read_csv(self.file_path, encoding='utf-8')
                    # Apply automatic migration
                    df = migrate_csv_schema(df, expected_schema, 'email_settings.csv')
                    # Save migrated schema
                    df.to_csv(self.file_path, index=False)
                    # Ensure it's not empty and has the correct ID
                    if not df.empty and df['id'].iloc[0] == 1:
                        return df
                except pd.errors.EmptyDataError:
                    # File appears empty to pandas - might be locked or corrupted
                    print(f"WARNING: {self.file_path} has {file_size} bytes but pandas sees no data.")
                    print(f"This might be a file lock issue. Retrying...")
                    import time
                    time.sleep(0.1)  # Wait 100ms for file lock to release
                    try:
                        df = pd.read_csv(self.file_path, encoding='utf-8')
                        df = migrate_csv_schema(df, expected_schema, 'email_settings.csv')
                        df.to_csv(self.file_path, index=False)
                        return df
                    except Exception as retry_error:
                        print(f"RETRY FAILED: {retry_error}")
                        # Fall through to create empty schema
                        df = pd.DataFrame(columns=list(expected_schema.keys()))
                        return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

            # File is very small (just headers or empty) - only recreate if truly empty
            elif file_size == 0:
                print(f"Info: {self.file_path} is completely empty (0 bytes). Creating with schema.")
                df = pd.DataFrame(columns=list(expected_schema.keys()))
                df.to_csv(self.file_path, index=False)
                return df
            else:
                # File has some content (likely just headers) - try to read
                try:
                    df = pd.read_csv(self.file_path, encoding='utf-8')
                    df = migrate_csv_schema(df, expected_schema, 'email_settings.csv')
                    df.to_csv(self.file_path, index=False)
                    return df
                except pd.errors.EmptyDataError:
                    # File has headers but no data rows - that's OK
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    df.to_csv(self.file_path, index=False)
                    return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

        # File doesn't exist - create new
        print(f"Info: {self.file_path} does not exist. Creating new file.")
        df = pd.DataFrame(columns=list(expected_schema.keys()))
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        df.to_csv(self.file_path, index=False)
        return df

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
        # Define expected schema with default values
        expected_schema = {
            'id': None,
            'user_id': None,
            'first_name_ar': None,
            'last_name_ar': None,
            'first_name_en': None,
            'last_name_en': None,
            'position_ar': None,
            'position_en': None,
            'unit_id': None,
            'manager_id': None,
            'start_date': None,
            'monthly_vacation_earned': 2.5,
            'signature_path': None,
            'contract_auto_renewed': False  # New field for contract management
        }

        if os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)

            # If file has content, try to read it
            if file_size > 100:  # More than just a header line
                try:
                    # CRITICAL: Force 'id' column to be string to preserve leading zeros (e.g., "0000001")
                    df = pd.read_csv(self.file_path, encoding='utf-8', dtype={'id': str})
                    # Apply automatic migration
                    df = migrate_csv_schema(df, expected_schema, 'employees.csv')
                    # Save migrated schema
                    df.to_csv(self.file_path, index=False)
                    return df
                except pd.errors.EmptyDataError:
                    # File appears empty to pandas - might be locked or corrupted
                    print(f"WARNING: {self.file_path} has {file_size} bytes but pandas sees no data.")
                    print(f"This might be a file lock issue. Retrying...")
                    import time
                    time.sleep(0.1)  # Wait 100ms for file lock to release
                    try:
                        df = pd.read_csv(self.file_path, encoding='utf-8', dtype={'id': str})
                        df = migrate_csv_schema(df, expected_schema, 'employees.csv')
                        df.to_csv(self.file_path, index=False)
                        return df
                    except Exception as retry_error:
                        print(f"RETRY FAILED: {retry_error}")
                        # Fall through to create empty schema
                        df = pd.DataFrame(columns=list(expected_schema.keys()))
                        return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

            # File is very small (just headers or empty) - only recreate if truly empty
            elif file_size == 0:
                print(f"Info: {self.file_path} is completely empty (0 bytes). Creating with schema.")
                df = pd.DataFrame(columns=list(expected_schema.keys()))
                df.to_csv(self.file_path, index=False)
                return df
            else:
                # File has some content (likely just headers) - try to read
                try:
                    # CRITICAL: Force 'id' column to be string to preserve leading zeros
                    df = pd.read_csv(self.file_path, encoding='utf-8', dtype={'id': str})
                    df = migrate_csv_schema(df, expected_schema, 'employees.csv')
                    df.to_csv(self.file_path, index=False)
                    return df
                except pd.errors.EmptyDataError:
                    # File has headers but no data rows - that's OK
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    df.to_csv(self.file_path, index=False)
                    return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

        # File doesn't exist - create new
        print(f"Info: {self.file_path} does not exist. Creating new file.")
        df = pd.DataFrame(columns=list(expected_schema.keys()))
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        df.to_csv(self.file_path, index=False)
        return df

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
        # Define expected schema with default values
        expected_schema = {
            'id': None,
            'employee_id': None,
            'vacation_type': None,
            'start_date': None,
            'end_date': None,
            'duration': 0,
            'status': 'Pending',
            'rejection_reason': None,
            'approval_date': None,
            'balance_used': 0,
            'attachments': '[]'  # Empty list as string
        }

        if os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)

            # If file has content, try to read it
            if file_size > 100:  # More than just a header line
                try:
                    df = pd.read_csv(self.file_path, encoding='utf-8')
                    # Apply automatic migration
                    df = migrate_csv_schema(df, expected_schema, 'leave_requests.csv')
                    # Save migrated schema
                    df.to_csv(self.file_path, index=False)

                    # Convert 'attachments' column from string to list
                    if 'attachments' in df.columns:
                        df['attachments'] = df['attachments'].apply(lambda x: eval(x) if pd.notna(x) else [])
                    return df
                except pd.errors.EmptyDataError:
                    # File appears empty to pandas - might be locked or corrupted
                    print(f"WARNING: {self.file_path} has {file_size} bytes but pandas sees no data.")
                    print(f"This might be a file lock issue. Retrying...")
                    import time
                    time.sleep(0.1)  # Wait 100ms for file lock to release
                    try:
                        df = pd.read_csv(self.file_path, encoding='utf-8')
                        df = migrate_csv_schema(df, expected_schema, 'leave_requests.csv')
                        df.to_csv(self.file_path, index=False)
                        if 'attachments' in df.columns:
                            df['attachments'] = df['attachments'].apply(lambda x: eval(x) if pd.notna(x) else [])
                        return df
                    except Exception as retry_error:
                        print(f"RETRY FAILED: {retry_error}")
                        # Fall through to create empty schema
                        df = pd.DataFrame(columns=list(expected_schema.keys()))
                        return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

            # File is very small (just headers or empty) - only recreate if truly empty
            elif file_size == 0:
                print(f"Info: {self.file_path} is completely empty (0 bytes). Creating with schema.")
                df = pd.DataFrame(columns=list(expected_schema.keys()))
                df.to_csv(self.file_path, index=False)
                return df
            else:
                # File has some content (likely just headers) - try to read
                try:
                    df = pd.read_csv(self.file_path, encoding='utf-8')
                    df = migrate_csv_schema(df, expected_schema, 'leave_requests.csv')
                    df.to_csv(self.file_path, index=False)
                    if 'attachments' in df.columns:
                        df['attachments'] = df['attachments'].apply(lambda x: eval(x) if pd.notna(x) else [])
                    return df
                except pd.errors.EmptyDataError:
                    # File has headers but no data rows - that's OK
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    df.to_csv(self.file_path, index=False)
                    return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

        # File doesn't exist - create new
        print(f"Info: {self.file_path} does not exist. Creating new file.")
        df = pd.DataFrame(columns=list(expected_schema.keys()))
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        df.to_csv(self.file_path, index=False)
        return df

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
        # Define expected schema with default values
        expected_schema = {
            'id': None,
            'name_en': None,
            'name_ar': None
        }

        if os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)

            # If file has content, try to read it
            if file_size > 100:  # More than just a header line
                try:
                    df = pd.read_csv(self.file_path, encoding='utf-8')
                    # Apply automatic migration
                    df = migrate_csv_schema(df, expected_schema, 'units.csv')
                    # Save migrated schema
                    df.to_csv(self.file_path, index=False)
                    return df
                except pd.errors.EmptyDataError:
                    # File appears empty to pandas - might be locked or corrupted
                    print(f"WARNING: {self.file_path} has {file_size} bytes but pandas sees no data.")
                    print(f"This might be a file lock issue. Retrying...")
                    import time
                    time.sleep(0.1)  # Wait 100ms for file lock to release
                    try:
                        df = pd.read_csv(self.file_path, encoding='utf-8')
                        df = migrate_csv_schema(df, expected_schema, 'units.csv')
                        df.to_csv(self.file_path, index=False)
                        return df
                    except Exception as retry_error:
                        print(f"RETRY FAILED: {retry_error}")
                        # Fall through to create empty schema
                        df = pd.DataFrame(columns=list(expected_schema.keys()))
                        return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

            # File is very small (just headers or empty) - only recreate if truly empty
            elif file_size == 0:
                print(f"Info: {self.file_path} is completely empty (0 bytes). Creating with schema.")
                df = pd.DataFrame(columns=list(expected_schema.keys()))
                df.to_csv(self.file_path, index=False)
                return df
            else:
                # File has some content (likely just headers) - try to read
                try:
                    df = pd.read_csv(self.file_path, encoding='utf-8')
                    df = migrate_csv_schema(df, expected_schema, 'units.csv')
                    df.to_csv(self.file_path, index=False)
                    return df
                except pd.errors.EmptyDataError:
                    # File has headers but no data rows - that's OK
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    df.to_csv(self.file_path, index=False)
                    return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

        # File doesn't exist - create new
        print(f"Info: {self.file_path} does not exist. Creating new file.")
        df = pd.DataFrame(columns=list(expected_schema.keys()))
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        df.to_csv(self.file_path, index=False)
        return df

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
        # Define expected schema with default values
        expected_schema = {
            'id': None,
            'employee_id': None,
            'date': None,
            'check_in': None,
            'check_out': None,
            'status': 'Present'
        }

        if os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)

            # If file has content (more than just headers), try to read it
            if file_size > 100:  # More than just a header line
                try:
                    df = pd.read_csv(self.file_path, encoding='utf-8')
                    # Apply automatic migration
                    df = migrate_csv_schema(df, expected_schema, 'attendance_logs.csv')
                    # Save migrated schema
                    df.to_csv(self.file_path, index=False)
                    return df
                except pd.errors.EmptyDataError:
                    # File appears empty to pandas - might be locked or corrupted
                    print(f"WARNING: {self.file_path} has {file_size} bytes but pandas sees no data.")
                    print(f"This might be a file lock issue. Retrying...")
                    import time
                    time.sleep(0.1)  # Wait 100ms for file lock to release
                    try:
                        df = pd.read_csv(self.file_path, encoding='utf-8')
                        df = migrate_csv_schema(df, expected_schema, 'attendance_logs.csv')
                        df.to_csv(self.file_path, index=False)
                        return df
                    except Exception as retry_error:
                        print(f"RETRY FAILED: {retry_error}")
                        # Fall through to create empty schema
                        df = pd.DataFrame(columns=list(expected_schema.keys()))
                        return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

            # File is very small (just headers or empty) - only recreate if truly empty
            elif file_size == 0:
                print(f"Info: {self.file_path} is completely empty (0 bytes). Creating with schema.")
                df = pd.DataFrame(columns=list(expected_schema.keys()))
                df.to_csv(self.file_path, index=False)
                return df
            else:
                # File has some content (likely just headers) - try to read
                try:
                    df = pd.read_csv(self.file_path, encoding='utf-8')
                    df = migrate_csv_schema(df, expected_schema, 'attendance_logs.csv')
                    df.to_csv(self.file_path, index=False)
                    return df
                except pd.errors.EmptyDataError:
                    # File has headers but no data rows - that's OK
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    df.to_csv(self.file_path, index=False)
                    return df
                except Exception as e:
                    # Other errors - might be corruption
                    print(f"ERROR: Cannot read {self.file_path} (size: {file_size} bytes). Error: {e}")
                    print(f"Attempting to recover by creating empty schema...")
                    df = pd.DataFrame(columns=list(expected_schema.keys()))
                    return df

        # File doesn't exist - create new
        print(f"Info: {self.file_path} does not exist. Creating new file.")
        df = pd.DataFrame(columns=list(expected_schema.keys()))
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        df.to_csv(self.file_path, index=False)
        return df

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