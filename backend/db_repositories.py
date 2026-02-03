"""
PostgreSQL Database Repositories using SQLAlchemy
Replaces CSV repositories with database-backed versions
Maintains same interface as CSVRepositories for compatibility
"""
from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from backend.database import (
    UserModel, EmployeeModel, UnitModel, LeaveRequestModel,
    AttendanceLogModel, EmailSettingsModel
)
from backend.models import (
    User, Employee, Unit, LeaveRequest, AttendanceLog, EmailSettings
)


class DBUserRepository:
    """PostgreSQL-backed user repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[User]:
        users = self.db.query(UserModel).all()
        return [User(
            id=u.id,
            email=u.email,
            password_hash=u.password_hash,
            role=u.role,
            is_active=u.is_active
        ) for u in users]

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            return User(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                role=user.role,
                is_active=user.is_active
            )
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if user:
            return User(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                role=user.role,
                is_active=user.is_active
            )
        return None

    def add(self, user: User) -> User:
        db_user = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            is_active=user.is_active
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return user

    def update(self, updated_user: User) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.id == updated_user.id).first()
        if db_user:
            db_user.email = updated_user.email
            db_user.password_hash = updated_user.password_hash
            db_user.role = updated_user.role
            db_user.is_active = updated_user.is_active
            self.db.commit()
            self.db.refresh(db_user)
        return updated_user

    def delete(self, user_id: UUID):
        self.db.query(UserModel).filter(UserModel.id == user_id).delete()
        self.db.commit()


class DBEmployeeRepository:
    """PostgreSQL-backed employee repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Employee]:
        employees = self.db.query(EmployeeModel).all()
        return [Employee(
            id=e.id,
            user_id=e.user_id,
            first_name_ar=e.first_name_ar,
            last_name_ar=e.last_name_ar,
            first_name_en=e.first_name_en,
            last_name_en=e.last_name_en,
            position_ar=e.position_ar,
            position_en=e.position_en,
            unit_id=e.unit_id,
            manager_id=e.manager_id,
            start_date=e.start_date,
            monthly_vacation_earned=e.monthly_vacation_earned,
            signature_path=e.signature_path,
            contract_auto_renewed=e.contract_auto_renewed
        ) for e in employees]

    def get_by_id(self, employee_id: str) -> Optional[Employee]:
        emp = self.db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
        if emp:
            return Employee(
                id=emp.id,
                user_id=emp.user_id,
                first_name_ar=emp.first_name_ar,
                last_name_ar=emp.last_name_ar,
                first_name_en=emp.first_name_en,
                last_name_en=emp.last_name_en,
                position_ar=emp.position_ar,
                position_en=emp.position_en,
                unit_id=emp.unit_id,
                manager_id=emp.manager_id,
                start_date=emp.start_date,
                monthly_vacation_earned=emp.monthly_vacation_earned,
                signature_path=emp.signature_path,
                contract_auto_renewed=emp.contract_auto_renewed
            )
        return None

    def get_by_user_id(self, user_id: UUID) -> Optional[Employee]:
        emp = self.db.query(EmployeeModel).filter(EmployeeModel.user_id == user_id).first()
        if emp:
            return Employee(
                id=emp.id,
                user_id=emp.user_id,
                first_name_ar=emp.first_name_ar,
                last_name_ar=emp.last_name_ar,
                first_name_en=emp.first_name_en,
                last_name_en=emp.last_name_en,
                position_ar=emp.position_ar,
                position_en=emp.position_en,
                unit_id=emp.unit_id,
                manager_id=emp.manager_id,
                start_date=emp.start_date,
                monthly_vacation_earned=emp.monthly_vacation_earned,
                signature_path=emp.signature_path,
                contract_auto_renewed=emp.contract_auto_renewed
            )
        return None

    def add(self, employee: Employee) -> Employee:
        # Convert empty string to None for optional foreign keys
        manager_id = employee.manager_id if employee.manager_id and employee.manager_id.strip() else None

        db_emp = EmployeeModel(
            id=employee.id,
            user_id=employee.user_id,
            first_name_ar=employee.first_name_ar,
            last_name_ar=employee.last_name_ar,
            first_name_en=employee.first_name_en,
            last_name_en=employee.last_name_en,
            position_ar=employee.position_ar,
            position_en=employee.position_en,
            unit_id=employee.unit_id,
            manager_id=manager_id,
            start_date=employee.start_date,
            monthly_vacation_earned=employee.monthly_vacation_earned,
            signature_path=employee.signature_path,
            contract_auto_renewed=employee.contract_auto_renewed
        )
        self.db.add(db_emp)
        self.db.commit()
        self.db.refresh(db_emp)
        return employee

    def update(self, updated_employee: Employee) -> Employee:
        # Extract employee_id from the employee object (matching service expectations)
        employee_id = updated_employee.id

        db_emp = self.db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
        if db_emp:
            # Convert empty string to None for optional foreign keys
            manager_id = updated_employee.manager_id if updated_employee.manager_id and updated_employee.manager_id.strip() else None

            db_emp.first_name_ar = updated_employee.first_name_ar
            db_emp.last_name_ar = updated_employee.last_name_ar
            db_emp.first_name_en = updated_employee.first_name_en
            db_emp.last_name_en = updated_employee.last_name_en
            db_emp.position_ar = updated_employee.position_ar
            db_emp.position_en = updated_employee.position_en
            db_emp.unit_id = updated_employee.unit_id
            db_emp.manager_id = manager_id
            db_emp.start_date = updated_employee.start_date
            db_emp.monthly_vacation_earned = updated_employee.monthly_vacation_earned
            db_emp.signature_path = updated_employee.signature_path
            db_emp.contract_auto_renewed = updated_employee.contract_auto_renewed
            self.db.commit()
            self.db.refresh(db_emp)
        return updated_employee

    def delete(self, employee_id: str):
        self.db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).delete()
        self.db.commit()


class DBUnitRepository:
    """PostgreSQL-backed unit repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Unit]:
        units = self.db.query(UnitModel).all()
        return [Unit(
            id=u.id,
            name_en=u.name_en,
            name_ar=u.name_ar
        ) for u in units]

    def get_by_id(self, unit_id: int) -> Optional[Unit]:
        unit = self.db.query(UnitModel).filter(UnitModel.id == unit_id).first()
        if unit:
            return Unit(
                id=unit.id,
                name_en=unit.name_en,
                name_ar=unit.name_ar
            )
        return None

    def add(self, unit: Unit) -> Unit:
        db_unit = UnitModel(
            name_en=unit.name_en,
            name_ar=unit.name_ar
        )
        self.db.add(db_unit)
        self.db.commit()
        self.db.refresh(db_unit)
        unit.id = db_unit.id  # Get auto-generated ID
        return unit

    def update(self, unit: Unit) -> Unit:
        db_unit = self.db.query(UnitModel).filter(UnitModel.id == unit.id).first()
        if db_unit:
            db_unit.name_en = unit.name_en
            db_unit.name_ar = unit.name_ar
            self.db.commit()
            self.db.refresh(db_unit)
        return unit

    def delete(self, unit_id: int):
        self.db.query(UnitModel).filter(UnitModel.id == unit_id).delete()
        self.db.commit()


class DBLeaveRequestRepository:
    """PostgreSQL-backed leave request repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[LeaveRequest]:
        requests = self.db.query(LeaveRequestModel).all()
        return [LeaveRequest(
            id=r.id,
            employee_id=r.employee_id,
            vacation_type=r.vacation_type,
            start_date=r.start_date,
            end_date=r.end_date,
            duration=r.duration,
            status=r.status,
            rejection_reason=r.rejection_reason,
            approval_date=r.approval_date,
            balance_used=r.balance_used,
            attachments=r.attachments if r.attachments else []
        ) for r in requests]

    def get_by_id(self, request_id: int) -> Optional[LeaveRequest]:
        req = self.db.query(LeaveRequestModel).filter(LeaveRequestModel.id == request_id).first()
        if req:
            return LeaveRequest(
                id=req.id,
                employee_id=req.employee_id,
                vacation_type=req.vacation_type,
                start_date=req.start_date,
                end_date=req.end_date,
                duration=req.duration,
                status=req.status,
                rejection_reason=req.rejection_reason,
                approval_date=req.approval_date,
                balance_used=req.balance_used,
                attachments=req.attachments if req.attachments else []
            )
        return None

    def get_by_employee_id(self, employee_id: str) -> List[LeaveRequest]:
        requests = self.db.query(LeaveRequestModel).filter(
            LeaveRequestModel.employee_id == employee_id
        ).all()
        return [LeaveRequest(
            id=r.id,
            employee_id=r.employee_id,
            vacation_type=r.vacation_type,
            start_date=r.start_date,
            end_date=r.end_date,
            duration=r.duration,
            status=r.status,
            rejection_reason=r.rejection_reason,
            approval_date=r.approval_date,
            balance_used=r.balance_used,
            attachments=r.attachments if r.attachments else []
        ) for r in requests]

    def add(self, leave_request: LeaveRequest) -> LeaveRequest:
        db_req = LeaveRequestModel(
            employee_id=leave_request.employee_id,
            vacation_type=leave_request.vacation_type,
            start_date=leave_request.start_date,
            end_date=leave_request.end_date,
            duration=leave_request.duration,
            status=leave_request.status,
            rejection_reason=leave_request.rejection_reason,
            approval_date=leave_request.approval_date,
            balance_used=leave_request.balance_used,
            attachments=leave_request.attachments if leave_request.attachments else []
        )
        self.db.add(db_req)
        self.db.commit()
        self.db.refresh(db_req)
        leave_request.id = db_req.id  # Get auto-generated ID
        return leave_request

    def update(self, updated_request: LeaveRequest) -> LeaveRequest:
        # Get request_id from the updated_request object
        request_id = updated_request.id

        db_req = self.db.query(LeaveRequestModel).filter(LeaveRequestModel.id == request_id).first()
        if db_req:
            db_req.vacation_type = updated_request.vacation_type
            db_req.start_date = updated_request.start_date
            db_req.end_date = updated_request.end_date
            db_req.duration = updated_request.duration
            db_req.status = updated_request.status
            db_req.rejection_reason = updated_request.rejection_reason
            db_req.approval_date = updated_request.approval_date
            db_req.balance_used = updated_request.balance_used
            db_req.attachments = updated_request.attachments if updated_request.attachments else []
            self.db.commit()
            self.db.refresh(db_req)
        return updated_request

    def delete(self, request_id: int):
        self.db.query(LeaveRequestModel).filter(LeaveRequestModel.id == request_id).delete()
        self.db.commit()


class DBAttendanceRepository:
    """PostgreSQL-backed attendance repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[AttendanceLog]:
        logs = self.db.query(AttendanceLogModel).all()
        return [AttendanceLog(
            id=log.id,
            employee_id=log.employee_id,
            date=log.date,
            check_in=log.check_in,
            check_out=log.check_out,
            status=log.status
        ) for log in logs]

    def get_by_employee_and_date(self, employee_id: str, date: str) -> Optional[AttendanceLog]:
        log = self.db.query(AttendanceLogModel).filter(
            AttendanceLogModel.employee_id == employee_id,
            AttendanceLogModel.date == date
        ).first()
        if log:
            return AttendanceLog(
                id=log.id,
                employee_id=log.employee_id,
                date=log.date,
                check_in=log.check_in,
                check_out=log.check_out,
                status=log.status
            )
        return None

    def add(self, attendance: AttendanceLog) -> AttendanceLog:
        db_log = AttendanceLogModel(
            id=attendance.id,
            employee_id=attendance.employee_id,
            date=attendance.date,
            check_in=attendance.check_in,
            check_out=attendance.check_out,
            status=attendance.status
        )
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return attendance

    def update(self, log_id: UUID, updated_log: AttendanceLog) -> AttendanceLog:
        db_log = self.db.query(AttendanceLogModel).filter(AttendanceLogModel.id == log_id).first()
        if db_log:
            db_log.check_out = updated_log.check_out
            db_log.status = updated_log.status
            self.db.commit()
            self.db.refresh(db_log)
        return updated_log


class DBEmailSettingsRepository:
    """PostgreSQL-backed email settings repository (singleton)"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[EmailSettings]:
        settings = self.db.query(EmailSettingsModel).first()
        if settings:
            return [EmailSettings(
                id=settings.id,
                smtp_host=settings.smtp_host,
                smtp_port=settings.smtp_port,
                smtp_username=settings.smtp_username,
                smtp_password_hash=settings.smtp_password_hash,
                sender_email=settings.sender_email,
                is_active=settings.is_active
            )]
        return []

    def get_by_id(self, settings_id: int) -> Optional[EmailSettings]:
        settings = self.db.query(EmailSettingsModel).filter(EmailSettingsModel.id == 1).first()
        if settings:
            return EmailSettings(
                id=settings.id,
                smtp_host=settings.smtp_host,
                smtp_port=settings.smtp_port,
                smtp_username=settings.smtp_username,
                smtp_password_hash=settings.smtp_password_hash,
                sender_email=settings.sender_email,
                is_active=settings.is_active
            )
        return None

    def add(self, settings: EmailSettings) -> EmailSettings:
        # Check if settings already exist
        existing = self.db.query(EmailSettingsModel).filter(EmailSettingsModel.id == 1).first()
        if existing:
            raise Exception("Email settings already configured. Use update instead.")

        db_settings = EmailSettingsModel(
            id=1,
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_username=settings.smtp_username,
            smtp_password_hash=settings.smtp_password_hash,
            sender_email=settings.sender_email,
            is_active=settings.is_active
        )
        self.db.add(db_settings)
        self.db.commit()
        self.db.refresh(db_settings)
        return settings

    def update(self, settings: EmailSettings) -> EmailSettings:
        db_settings = self.db.query(EmailSettingsModel).filter(EmailSettingsModel.id == 1).first()
        if db_settings:
            db_settings.smtp_host = settings.smtp_host
            db_settings.smtp_port = settings.smtp_port
            db_settings.smtp_username = settings.smtp_username
            db_settings.smtp_password_hash = settings.smtp_password_hash
            db_settings.sender_email = settings.sender_email
            db_settings.is_active = settings.is_active
            self.db.commit()
            self.db.refresh(db_settings)
        return settings
