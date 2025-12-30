from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    password_hash: str
    role: str # 'admin', 'manager', 'employee'
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

class Employee(BaseModel):
    id: str  # "IAU-001"
    user_id: UUID
    first_name_ar: str
    last_name_ar: str
    first_name_en: str
    last_name_en: str
    position_ar: str
    position_en: str
    unit_id: int
    manager_id: Optional[str] = None
    start_date: str # YYYY-MM-DD
    monthly_vacation_earned: float = 2.5
    signature_path: Optional[str] = None

class EmployeeWithBalance(Employee):
    vacation_balance: float
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    contract_end_date: Optional[str] = None
    days_remaining_in_contract: Optional[int] = None

class AttendanceLog(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    employee_id: str
    date: str  # YYYY-MM-DD
    check_in: datetime
    check_out: Optional[datetime] = None
    status: str  # 'Present', 'Absent', 'Late'


class LeaveRequest(BaseModel):
    id: int
    employee_id: str
    vacation_type: str  # e.g., 'Annual', 'Sick'
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    duration: int
    status: str = 'Pending'  # 'Pending', 'Approved', 'Rejected'
    rejection_reason: Optional[str] = None
    approval_date: Optional[str] = None
    balance_used: int
    attachments: List[str] = Field(default_factory=list) # List of file paths

class Unit(BaseModel):
    id: int
    name_en: str
    name_ar: str

class UnitCreate(BaseModel):
    name_en: str
    name_ar: str

class UnitUpdate(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None

class LeaveRequestCreate(BaseModel):
    vacation_type: str
    start_date: str # YYYY-MM-DD
    end_date: str # YYYY-MM-DD
    attachments: List[str] = Field(default_factory=list) # Optional attachments

class LeaveRequestUpdate(BaseModel):
    status: Optional[str] = None
    rejection_reason: Optional[str] = None
    attachments: Optional[List[str]] = None # Allow updating attachments


class AdminInit(BaseModel):
    email: EmailStr
    password: str
    first_name_ar: str
    last_name_ar: str
    first_name_en: str
    last_name_en: str

class EmployeeCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
    employee_id: Optional[str] = None  # Custom employee ID (e.g., IAU-006)
    first_name_ar: str
    last_name_ar: str
    first_name_en: str
    last_name_en: str
    position_ar: str
    position_en: str
    unit_id: Optional[int] = None
    start_date: Optional[str] = None  # YYYY-MM-DD
    monthly_vacation_earned: Optional[float] = 2.5
    manager_id: Optional[str] = None

class EmployeeUpdate(BaseModel):
    employee_id: Optional[str] = None  # Allow changing employee ID (admin only)
    first_name_ar: Optional[str] = None
    last_name_ar: Optional[str] = None
    first_name_en: Optional[str] = None
    last_name_en: Optional[str] = None
    position_ar: Optional[str] = None
    position_en: Optional[str] = None
    unit_id: Optional[int] = None
    start_date: Optional[str] = None
    manager_id: Optional[str] = None
    monthly_vacation_earned: Optional[float] = None
    role: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class SignatureUpload(BaseModel):
    image_base64: str

# Email Settings Models
class EmailSettings(BaseModel):
    # Fixed ID since there's only one set of settings
    id: int = 1 
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password_hash: str # Hashed password for security
    sender_email: EmailStr
    is_active: bool = False

class EmailSettingsCreate(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str # Plain password for creation, will be hashed
    sender_email: EmailStr
    is_active: bool = False

class EmailSettingsUpdate(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None # Plain password for update, will be hashed
    sender_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

# Dashboard Report Models
class DashboardReportRequest(BaseModel):
    filter_type: str  # 'ytd', 'custom', 'last_30', 'last_60', 'last_90', 'full_year'
    start_date: Optional[str] = None  # YYYY-MM-DD for custom range
    end_date: Optional[str] = None  # YYYY-MM-DD for custom range
    language: str = 'en'  # 'en' or 'ar'
    date_system: str = 'gregorian'  # 'gregorian' or 'hijri'

class TeamMemberStats(BaseModel):
    name_en: str
    name_ar: str
    total_leaves_taken: int
    vacation_balance: float
    current_status: str  # 'Present', 'On Leave'
    leaves_by_type: dict  # {'Annual': 5, 'Sick': 2, 'Emergency': 1}
