
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .db_repositories import (
    DBUserRepository, DBEmployeeRepository, DBLeaveRequestRepository,
    DBUnitRepository, DBAttendanceRepository, DBEmailSettingsRepository
)
from .services import UserService, EmployeeService, LeaveRequestService, UnitService, AttendanceService, EmailSettingsService
from .email_service import EmailService

# --- Dependency Injection setup (PostgreSQL) ---

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = DBUserRepository(db)
    employee_repo = DBEmployeeRepository(db)
    return UserService(user_repo, employee_repo)

def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    employee_repo = DBEmployeeRepository(db)
    user_repo = DBUserRepository(db)
    leave_request_repo = DBLeaveRequestRepository(db)
    return EmployeeService(employee_repo, user_repo, leave_request_repo)

def get_leave_request_service(db: Session = Depends(get_db)) -> LeaveRequestService:
    leave_request_repo = DBLeaveRequestRepository(db)
    employee_service = get_employee_service(db)
    return LeaveRequestService(leave_request_repo, employee_service)

def get_unit_service(db: Session = Depends(get_db)) -> UnitService:
    unit_repo = DBUnitRepository(db)
    return UnitService(unit_repo)

def get_attendance_service(db: Session = Depends(get_db)) -> AttendanceService:
    attendance_repo = DBAttendanceRepository(db)
    employee_service = get_employee_service(db)
    leave_request_repo = DBLeaveRequestRepository(db)
    return AttendanceService(attendance_repo, employee_service, leave_request_repo)

def get_email_service() -> EmailService:
    return EmailService()

def get_email_settings_service(db: Session = Depends(get_db)) -> EmailSettingsService:
    email_settings_repo = DBEmailSettingsRepository(db)
    return EmailSettingsService(email_settings_repo)
