
from fastapi import Depends
from .repositories import CSVUserRepository, CSVEmployeeRepository, CSVLeaveRequestRepository, CSVUnitRepository, CSVAttendanceRepository
from .services import UserService, EmployeeService, LeaveRequestService, UnitService, AttendanceService
from .email_service import EmailService

# --- Dependency Injection setup ---
def get_user_service() -> UserService:
    user_repo = CSVUserRepository()
    employee_repo = CSVEmployeeRepository()
    return UserService(user_repo, employee_repo)

def get_employee_service() -> EmployeeService:
    employee_repo = CSVEmployeeRepository()
    user_repo = CSVUserRepository()
    leave_request_repo = CSVLeaveRequestRepository()
    return EmployeeService(employee_repo, user_repo, leave_request_repo)

def get_leave_request_service(
    leave_request_repo: CSVLeaveRequestRepository = Depends(CSVLeaveRequestRepository),
    employee_service: EmployeeService = Depends(get_employee_service)
) -> LeaveRequestService:
    return LeaveRequestService(leave_request_repo, employee_service)

def get_unit_service() -> UnitService:
    unit_repo = CSVUnitRepository()
    return UnitService(unit_repo)

def get_attendance_service(
    employee_service: EmployeeService = Depends(get_employee_service),
    leave_request_repo: CSVLeaveRequestRepository = Depends(CSVLeaveRequestRepository)
) -> AttendanceService:
    attendance_repo = CSVAttendanceRepository()
    return AttendanceService(attendance_repo, employee_service, leave_request_repo)

def get_email_service() -> EmailService:
    return EmailService()

from .repositories import CSVEmailSettingsRepository
from .services import EmailSettingsService

def get_email_settings_service(
    email_settings_repo: CSVEmailSettingsRepository = Depends(CSVEmailSettingsRepository)
) -> EmailSettingsService:
    return EmailSettingsService(email_settings_repo)
