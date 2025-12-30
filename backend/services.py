from .repositories import CSVUserRepository, CSVEmployeeRepository, CSVLeaveRequestRepository, CSVUnitRepository, CSVAttendanceRepository, CSVEmailSettingsRepository
from .models import User, UserCreate, Employee, EmployeeCreate, EmployeeWithBalance, LeaveRequest, LeaveRequestCreate, LeaveRequestUpdate, AdminInit, Unit, EmployeeUpdate, UnitCreate, UnitUpdate, AttendanceLog, EmailSettings, EmailSettingsCreate, EmailSettingsUpdate
from .email_templates import (
    render_leave_request_created_email,
    render_leave_request_approved_email
)
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, date
from .password import verify_password, get_password_hash, verify_password_raw
from .calculation import calculate_vacation_balance, get_current_contract_period
from .image_utils import optimize_signature_image
import base64
import os
import shutil
import mimetypes
from pathlib import Path
import smtplib
from email.message import EmailMessage
import logging

# Directory for attachments
ATTACHMENTS_DIR = Path("backend/data/attachments")
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)

# Directory for signatures
SIGNATURES_DIR = Path("backend/data/signatures")
os.makedirs(SIGNATURES_DIR, exist_ok=True)

def save_attachment(file_content: bytes, filename: str, employee_id: str) -> str:
    """Saves a file to the attachments directory and returns its path."""
    # Ensure directory for employee exists
    employee_attachments_dir = ATTACHMENTS_DIR / employee_id
    os.makedirs(employee_attachments_dir, exist_ok=True)

    # Sanitize filename (basic sanitation, more robust needed for production)
    safe_filename = "".join(c for c in filename if c.isalnum() or c in ('.', '_', '-')).rstrip()
    if not safe_filename:
        safe_filename = f"{uuid4()}" # Fallback to UUID if filename is empty after sanitization
    
    # Prepend UUID to avoid name collisions and ensure uniqueness
    final_filename = f"{uuid4()}_{safe_filename}"
    file_path = employee_attachments_dir / final_filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    return str(file_path) # Return string representation for storage

class UserService:
    def __init__(self, user_repository: CSVUserRepository, employee_repository: CSVEmployeeRepository):
        self.user_repository = user_repository
        self.employee_repository = employee_repository

    def get_users(self) -> List[User]:
        return self.user_repository.get_all()

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repository.get_by_email(email)

    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise Exception("User not found")
        if not verify_password(current_password, user.password_hash):
            raise Exception("Incorrect current password")
        
        user.password_hash = get_password_hash(new_password)
        self.user_repository.update(user)
        return True

    def initialize_first_user(self, admin_init: AdminInit) -> User:
        if self.get_users():
            raise Exception("Cannot initialize admin user, as users already exist.")

        hashed_password = get_password_hash(admin_init.password)
        admin_user = User(
            email=admin_init.email,
            password_hash=hashed_password,
            role="admin"
        )
        created_user = self.user_repository.add(admin_user)

        all_employees = self.employee_repository.get_all()
        next_id_num = len(all_employees) + 1
        
        admin_employee = Employee(
            id=f"IAU-{next_id_num:03d}",
            user_id=created_user.id,
            first_name_ar=admin_init.first_name_ar,
            last_name_ar=admin_init.last_name_ar,
            first_name_en=admin_init.first_name_en,
            last_name_en=admin_init.last_name_en,
            position_ar="مسؤول النظام",
            position_en="System Admin",
            unit_id=1, # Default to 'Administritive affairs'
            start_date="2024-01-01",
        )
        self.employee_repository.add(admin_employee)
        
        return created_user

    def create_user(self, user_create: UserCreate) -> User:
        # Normalize email to lowercase
        email_lower = user_create.email.lower()

        hashed_password = get_password_hash(user_create.password)
        user = User(
            email=email_lower,
            password_hash=hashed_password,
            role=user_create.role
        )
        return self.user_repository.add(user)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        # Convert email to lowercase for case-insensitive comparison
        email_lower = email.lower()

        user = self.user_repository.get_by_email(email_lower)
        if not user:
            # Fallback: Check all users with case-insensitive comparison
            all_users = self.user_repository.get_all()
            user = next((u for u in all_users if u.email.lower() == email_lower), None)

        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def delete_user(self, user_id: UUID):
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise Exception("User not found")
        
        # Find associated employee
        employee = self.employee_repository.get_by_user_id(user_id)
        if employee:
            self.employee_repository.delete(employee.id)
            
        self.user_repository.delete(user_id)

class EmployeeService:
    def __init__(self, employee_repository: CSVEmployeeRepository, user_repository: CSVUserRepository, leave_request_repository: CSVLeaveRequestRepository):
        self.employee_repository = employee_repository
        self.user_repository = user_repository
        self.leave_request_repository = leave_request_repository

    def _get_employee_with_balance(self, employee: Employee) -> EmployeeWithBalance:
        if not employee:
            return None
        
        all_requests = self.leave_request_repository.get_all()
        approved_requests = [req for req in all_requests if req.status == 'Approved' and req.employee_id == employee.id]
        
        balance = calculate_vacation_balance(employee, approved_requests)
        
        employee_data = employee.dict()
        employee_data['vacation_balance'] = balance

        # Contract Details
        try:
            start_date_obj = datetime.strptime(employee.start_date, "%Y-%m-%d").date()
            _, contract_end = get_current_contract_period(start_date_obj, date.today())
            employee_data['contract_end_date'] = contract_end.isoformat()
            employee_data['days_remaining_in_contract'] = (contract_end - date.today()).days
        except Exception:
            pass # Handle potential parsing errors gracefully

        # Fetch user details (role, email)
        user = self.user_repository.get_by_id(employee.user_id)
        if user:
            employee_data['role'] = user.role
            employee_data['email'] = user.email
        
        return EmployeeWithBalance(**employee_data)

    def get_employees(self) -> List[EmployeeWithBalance]:
        employees = self.employee_repository.get_all()
        return [self._get_employee_with_balance(emp) for emp in employees]

    def get_employee_by_id(self, employee_id: str) -> Optional[EmployeeWithBalance]:
        employee = self.employee_repository.get_by_id(employee_id)
        return self._get_employee_with_balance(employee)
    
    def get_employee_by_user_id(self, user_id: UUID) -> Optional[EmployeeWithBalance]:
        employee = self.employee_repository.get_by_user_id(user_id)
        return self._get_employee_with_balance(employee)

    def update_employee(self, employee_id: str, update_data: EmployeeUpdate) -> EmployeeWithBalance:
        import os
        from pathlib import Path
        import logging
        # Force reload
        employee = self.employee_repository.get_by_id(employee_id)
        if not employee:
            raise Exception("Employee not found")

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        role_update = update_dict.pop('role', None)
        new_employee_id = update_dict.pop('employee_id', None)

        # Handle employee ID change (requires updating related records)
        if new_employee_id and new_employee_id != employee_id:
            # Check for duplicate
            if self.employee_repository.get_by_id(new_employee_id):
                raise Exception(f"Employee ID '{new_employee_id}' already exists")

            # Update leave requests that reference this employee
            from .repositories import CSVLeaveRequestRepository
            leave_repo = CSVLeaveRequestRepository()
            all_requests = leave_repo.get_all()
            for req in all_requests:
                if req.employee_id == employee_id:
                    req.employee_id = new_employee_id
                    leave_repo.update(req)

            # Update manager references in other employees
            all_employees = self.employee_repository.get_all()
            for emp in all_employees:
                if emp.manager_id == employee_id:
                    emp.manager_id = new_employee_id
                    # For other employees, we update them separately with old ID
                    self.employee_repository.update(emp)

            # Rename signature file if it exists
            old_sig_path = Path(f"backend/data/signatures/{employee_id}_signature.png")
            new_sig_path = Path(f"backend/data/signatures/{new_employee_id}_signature.png")
            if old_sig_path.exists():
                old_sig_path.rename(new_sig_path)
                employee.signature_path = str(new_sig_path)

            # Apply other field updates first (before changing ID)
            for key, value in update_dict.items():
                setattr(employee, key, value)

            # Update the employee record with OLD ID first
            self.employee_repository.update(employee)

            # Now delete old record and create new one with new ID
            self.employee_repository.delete(employee_id)

            employee.id = new_employee_id
            self.employee_repository.add(employee)
        else:
            # Normal update without ID change
            for key, value in update_dict.items():
                setattr(employee, key, value)
            self.employee_repository.update(employee)

        # Update User role if provided
        if role_update:
            user = self.user_repository.get_by_id(employee.user_id)
            if user:
                user.role = role_update
                self.user_repository.update(user)

        return self._get_employee_with_balance(employee)

    def get_team_members(self, manager_id: str, include_indirect: bool = True) -> List[EmployeeWithBalance]:
        """
        Get all team members for a manager (direct and indirect reports).

        Args:
            manager_id: The manager's employee ID
            include_indirect: If True, includes subordinates of subordinates

        Returns:
            List of EmployeeWithBalance objects for all team members
        """
        from backend.hierarchy import get_all_subordinates

        all_employees = self.get_employees()
        subordinate_ids = get_all_subordinates(manager_id, all_employees, include_indirect)

        return [emp for emp in all_employees if emp.id in subordinate_ids]

    def check_and_renew_expired_contracts(self) -> List[EmployeeWithBalance]:
        """
        Check for expired contracts and auto-renew them.
        Returns list of employees whose contracts were auto-renewed.
        """
        from datetime import datetime, timedelta

        all_employees = self.get_employees()
        today = datetime.now().date()
        renewed_employees = []

        for emp in all_employees:
            if emp.contract_end_date and emp.contract_end_date != 'N/A':
                try:
                    contract_end = datetime.strptime(emp.contract_end_date, '%Y-%m-%d').date()

                    # If contract has expired, auto-renew it
                    if contract_end <= today:
                        # Get the actual employee record
                        employee = self.employee_repository.get_by_id(emp.id)
                        if employee:
                            # Set new contract end date to 1 year from old date
                            new_end_date = contract_end + timedelta(days=365)
                            employee.contract_end_date = new_end_date.strftime('%Y-%m-%d')
                            employee.contract_auto_renewed = True

                            # Update in repository
                            self.employee_repository.update(employee)

                            # Get updated employee with balance
                            renewed_emp = self._get_employee_with_balance(employee)
                            renewed_employees.append(renewed_emp)

                except Exception as e:
                    continue

        return renewed_employees

    def get_employees_with_expiring_contracts(self, days_threshold: int = 105) -> List[EmployeeWithBalance]:
        """
        Get employees whose contracts are expiring within the threshold days.
        Returns list of employees with expiring contracts.
        """
        from datetime import datetime, timedelta

        all_employees = self.get_employees()
        today = datetime.now().date()
        expiring_employees = []

        for emp in all_employees:
            if emp.contract_end_date and emp.contract_end_date != 'N/A' and emp.days_remaining_in_contract:
                if 0 < emp.days_remaining_in_contract <= days_threshold:
                    expiring_employees.append(emp)

        return expiring_employees

    def get_employees_needing_contract_verification(self) -> List[EmployeeWithBalance]:
        """
        Get employees whose contracts were auto-renewed and need manager verification.
        """
        all_employees = self.get_employees()
        return [emp for emp in all_employees if emp.contract_auto_renewed]

    def clear_contract_verification_flag(self, employee_id: str) -> None:
        """
        Clear the contract auto-renewed flag when manager verifies the contract.
        """
        employee = self.employee_repository.get_by_id(employee_id)
        if employee:
            employee.contract_auto_renewed = False
            self.employee_repository.update(employee)

    def create_user_and_employee(self, employee_create: EmployeeCreate) -> EmployeeWithBalance:
        if self.user_repository.get_by_email(employee_create.email):
            raise Exception("User with this email already exists.")

        # For non-admin roles, require unit_id, manager_id, and start_date
        if employee_create.role != "admin":
            if not employee_create.unit_id:
                raise Exception("Unit is required for non-admin roles")
            if not employee_create.manager_id:
                raise Exception("Manager is required for non-admin roles")
            if not employee_create.start_date:
                raise Exception("Start date is required for non-admin roles")

        hashed_password = get_password_hash(employee_create.password)
        new_user = User(
            email=employee_create.email,
            password_hash=hashed_password,
            role=employee_create.role
        )
        created_user = self.user_repository.add(new_user)

        all_employees = self.employee_repository.get_all()

        # Use provided employee_id or generate new one
        if employee_create.employee_id:
            # Check for duplicate employee IDs
            if any(emp.id == employee_create.employee_id for emp in all_employees):
                raise Exception(f"Employee ID '{employee_create.employee_id}' already exists")
            employee_id = employee_create.employee_id
        else:
            # Robust ID generation
            max_id_num = 0
            for emp in all_employees:
                try:
                    num_part = int(emp.id.split('-')[1])
                    if num_part > max_id_num:
                        max_id_num = num_part
                except (IndexError, ValueError):
                    continue

            next_id_num = max_id_num + 1
            employee_id = f"IAU-{next_id_num:03d}"

        new_employee = Employee(
            id=employee_id,
            user_id=created_user.id,
            **employee_create.dict(exclude={'email', 'password', 'role', 'employee_id'})
        )
        created_employee = self.employee_repository.add(new_employee)
        
        return self._get_employee_with_balance(created_employee)

    def upload_signature(self, user_id: UUID, base64_image: str) -> str:
        employee = self.employee_repository.get_by_user_id(user_id)
        if not employee:
            raise Exception("Employee profile not found")

        # Optimize signature image
        optimized_bytes = optimize_signature_image(base64_image, max_width=600)

        # Save as PNG (optimization always outputs PNG)
        filename = f"{employee.id}_signature.png"
        file_path = SIGNATURES_DIR / filename

        with open(file_path, "wb") as f:
            f.write(optimized_bytes)

        # Update employee record
        employee.signature_path = str(file_path)
        self.employee_repository.update(employee)

        return str(file_path)

class LeaveRequestService:
    def __init__(self, leave_request_repository: CSVLeaveRequestRepository, employee_service: EmployeeService):
        self.leave_request_repository = leave_request_repository
        self.employee_service = employee_service

    def get_leave_requests(self) -> List[LeaveRequest]:
        return self.leave_request_repository.get_all()

    def get_leave_request_by_id(self, leave_request_id: int) -> Optional[LeaveRequest]:
        return self.leave_request_repository.get_by_id(leave_request_id)

    def create_leave_request(self, leave_request_create: LeaveRequestCreate, user_id: UUID) -> LeaveRequest:
        employee = self.employee_service.get_employee_by_user_id(user_id)
        if not employee:
            raise Exception("No employee profile found for current user.") # Or a more specific HTTP exception

        start_date_obj = datetime.strptime(leave_request_create.start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(leave_request_create.end_date, "%Y-%m-%d").date()
        duration = (end_date_obj - start_date_obj).days + 1

        all_requests = self.leave_request_repository.get_all()
        new_id = max([req.id for req in all_requests]) + 1 if all_requests else 1
        
        leave_request = LeaveRequest(
            id=new_id,
            employee_id=employee.id, # Use the authenticated user's employee ID
            vacation_type=leave_request_create.vacation_type,
            start_date=leave_request_create.start_date,
            end_date=leave_request_create.end_date,
            duration=duration,
            balance_used=duration, # TODO: Check against balance
            status='Pending',
            attachments=leave_request_create.attachments # Save attachment paths
        )

        created_request = self.leave_request_repository.add(leave_request)

        # Send notification to manager
        try:
            if employee.manager_id:
                manager = self.employee_service.get_employee_by_id(employee.manager_id)

                if manager:
                    # Get manager's email from user record
                    from .dependencies import get_email_service
                    email_service = get_email_service()

                    # Get user records to fetch emails
                    manager_user = self.employee_service.user_repository.get_by_id(manager.user_id)

                    if manager_user and manager_user.email:
                        email_data = {
                            'employee_name_ar': f"{employee.first_name_ar} {employee.last_name_ar}",
                            'employee_name_en': f"{employee.first_name_en} {employee.last_name_en}",
                            'employee_id': employee.id,
                            'vacation_type': leave_request_create.vacation_type,
                            'start_date': leave_request_create.start_date,
                            'end_date': leave_request_create.end_date,
                            'duration': duration,
                            'manager_name_ar': f"{manager.first_name_ar} {manager.last_name_ar}",
                            'manager_name_en': f"{manager.first_name_en} {manager.last_name_en}"
                        }

                        html_body = render_leave_request_created_email(email_data)
                        email_service.send_email(
                            to_email=manager_user.email,
                            subject="New Leave Request / طلب إجازة جديد",
                            body=html_body,
                            is_html=True
                        )
                        logging.info(f"Leave request notification sent to manager {manager_user.email}")
        except Exception as e:
            logging.error(f"Failed to send manager notification: {str(e)}")

        return created_request

    def update_leave_request(self, leave_request_id: int, leave_request_update: LeaveRequestUpdate) -> Optional[LeaveRequest]:
        leave_request = self.leave_request_repository.get_by_id(leave_request_id)
        if not leave_request:
            return None

        if leave_request_update.status:
            leave_request.status = leave_request_update.status
            if leave_request.status == 'Approved':
                leave_request.approval_date = date.today().isoformat()

                # Send approval notification to employee
                try:
                    employee = self.employee_service.get_employee_by_id(leave_request.employee_id)
                    if employee:
                        # Get employee's email from user record
                        from .dependencies import get_email_service
                        email_service = get_email_service()

                        employee_user = self.employee_service.user_repository.get_by_id(employee.user_id)

                        if employee_user and employee_user.email:
                            remaining_balance = employee.vacation_balance - leave_request.balance_used

                            email_data = {
                                'employee_name_ar': f"{employee.first_name_ar} {employee.last_name_ar}",
                                'employee_name_en': f"{employee.first_name_en} {employee.last_name_en}",
                                'vacation_type': leave_request.vacation_type,
                                'start_date': leave_request.start_date,
                                'end_date': leave_request.end_date,
                                'duration': leave_request.duration,
                                'balance_deducted': leave_request.balance_used,
                                'remaining_balance': remaining_balance
                            }

                            html_body = render_leave_request_approved_email(email_data)
                            email_service.send_email(
                                to_email=employee_user.email,
                                subject="Leave Request Approved / تمت الموافقة على طلب الإجازة",
                                body=html_body,
                                is_html=True
                            )
                            logging.info(f"Approval notification sent to employee {employee_user.email}")
                except Exception as e:
                    logging.error(f"Failed to send approval notification: {str(e)}")
            elif leave_request.status == 'Rejected':
                leave_request.rejection_reason = leave_request_update.rejection_reason
        
        if leave_request_update.attachments is not None:
            leave_request.attachments = leave_request_update.attachments
            
        return self.leave_request_repository.update(leave_request)

class UnitService:
    def __init__(self, unit_repository: CSVUnitRepository):
        self.unit_repository = unit_repository

    def get_units(self) -> List[Unit]:
        return self.unit_repository.get_all()

    def create_unit(self, unit_create: UnitCreate) -> Unit:
        all_units = self.unit_repository.get_all()
        new_id = max([u.id for u in all_units]) + 1 if all_units else 1
        
        unit = Unit(
            id=new_id,
            name_en=unit_create.name_en,
            name_ar=unit_create.name_ar
        )
        return self.unit_repository.add(unit)

    def update_unit(self, unit_id: int, unit_update: UnitUpdate) -> Unit:
        unit = self.unit_repository.get_by_id(unit_id)
        if not unit:
            raise Exception("Unit not found")

        if unit_update.name_en:
            unit.name_en = unit_update.name_en
        if unit_update.name_ar:
            unit.name_ar = unit_update.name_ar

        return self.unit_repository.update(unit)

    def delete_unit(self, unit_id: int) -> None:
        """Delete a unit by ID"""
        unit = self.unit_repository.get_by_id(unit_id)
        if not unit:
            raise Exception("Unit not found")
        self.unit_repository.delete(unit_id)

class AttendanceService:
    def __init__(self, attendance_repository: CSVAttendanceRepository, employee_service: EmployeeService, leave_request_repository: CSVLeaveRequestRepository):
        self.attendance_repository = attendance_repository
        self.employee_service = employee_service
        self.leave_request_repository = leave_request_repository

    def get_today_status(self, user_id: UUID) -> dict:
        employee = self.employee_service.get_employee_by_user_id(user_id)
        if not employee:
            return {"status": "Unknown"}
        
        today = date.today()

        # Check for approved leave
        all_requests = self.leave_request_repository.get_all()
        for req in all_requests:
            if req.employee_id == employee.id and req.status == 'Approved':
                start = datetime.strptime(req.start_date, "%Y-%m-%d").date()
                end = datetime.strptime(req.end_date, "%Y-%m-%d").date()
                if start <= today <= end:
                    return {"status": "On Leave", "vacation_type": req.vacation_type}

        return {"status": "Present"}

class EmailSettingsService:
    def __init__(self, email_settings_repository: CSVEmailSettingsRepository):
        self.email_settings_repository = email_settings_repository
        
    def get_email_settings(self) -> Optional[EmailSettings]:
        return self.email_settings_repository.get_by_id(1) # Always ID 1

    def create_email_settings(self, settings_create: EmailSettingsCreate) -> EmailSettings:
        # Hash password before storing
        hashed_password = get_password_hash(settings_create.smtp_password)
        settings = EmailSettings(
            smtp_host=settings_create.smtp_host,
            smtp_port=settings_create.smtp_port,
            smtp_username=settings_create.smtp_username,
            smtp_password_hash=hashed_password,
            sender_email=settings_create.sender_email,
            is_active=settings_create.is_active
        )
        return self.email_settings_repository.add(settings)

    def update_email_settings(self, settings_update: EmailSettingsUpdate) -> EmailSettings:
        existing_settings = self.get_email_settings()
        if not existing_settings:
            raise Exception("Email settings not found. Please create them first.")
        
        update_data = settings_update.dict(exclude_unset=True)
        
        # Handle password hashing if provided
        if 'smtp_password' in update_data and update_data['smtp_password']:
            update_data['smtp_password_hash'] = get_password_hash(update_data.pop('smtp_password'))
        
        updated_settings = existing_settings.copy(update=update_data)
        return self.email_settings_repository.update(updated_settings)

    def delete_email_settings(self):
        self.email_settings_repository.delete(1)

    def test_smtp_connection(self, settings_create: EmailSettingsCreate) -> bool:
        """
        Tests SMTP connection with provided credentials.
        """
        try:
            with smtplib.SMTP(settings_create.smtp_host, settings_create.smtp_port) as server:
                server.starttls()
                server.login(settings_create.smtp_username, settings_create.smtp_password)
                return True
        except Exception as e:
            print(f"SMTP connection test failed: {e}")
            raise Exception(f"SMTP connection test failed: {e}")

    def send_email(self, recipient_email: str, subject: str, body: str):
        settings = self.get_email_settings()
        if not settings or not settings.is_active:
            raise Exception("Email service is not active or not configured.")
        
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = settings.sender_email
            msg['To'] = recipient_email
            msg.set_content(body)

            # Need to get raw password from hash for sending, not ideal for security
            # but required for standard smtplib. We should investigate a better way
            # with an encrypted field in the DB rather than hash.
            # For this prototype, if the user explicitly saves a password, it's hashed.
            # When we try to send, we have no way to get the raw password back.
            # This is a critical security flaw for production.
            # For testing and current scope, the only way to send is if the plaintext password
            # is temporarily provided or if we make `verify_password_raw` also decrypt.
            # For now, this send_email method won't be functional without a plaintext password.
            # The test_smtp_connection will work with plaintext from frontend.
            # TODO: Re-evaluate email sending for production security.

            # Temporarily, just return True for mocking success if active.
            print(f"MOCK EMAIL: To: {recipient_email}, Subject: {subject}, Body: {body}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            raise Exception(f"Error sending email: {e}")

    def send_contract_expiring_notification(self, manager_email: str, manager_name_ar: str, manager_name_en: str,
                                           employee_name_ar: str, employee_name_en: str, employee_id: str,
                                           contract_end_date: str, days_remaining: int):
        """
        Send email notification to manager when employee's contract is expiring within 105 days
        """
        from backend.email_templates import render_contract_expiring_manager_notification

        settings = self.get_email_settings()
        if not settings or not settings.is_active:
            print("Email service not active - skipping contract expiring notification")
            return

        html_body = render_contract_expiring_manager_notification({
            'manager_name_ar': manager_name_ar,
            'manager_name_en': manager_name_en,
            'employee_name_ar': employee_name_ar,
            'employee_name_en': employee_name_en,
            'employee_id': employee_id,
            'contract_end_date': contract_end_date,
            'days_remaining': days_remaining
        })

        subject = f"Contract Renewal Required / مطلوب تجديد العقد - {employee_name_en}"

        # For now, mock the email sending (same as existing send_email method)
        print(f"MOCK EMAIL: To: {manager_email}, Subject: {subject}")
        print(f"Contract expiring notification sent for employee {employee_id}")
        return True

    def send_contract_auto_renewed_notification(self, manager_email: str, manager_name_ar: str, manager_name_en: str,
                                               employee_name_ar: str, employee_name_en: str, employee_id: str,
                                               new_contract_end_date: str):
        """
        Send email notification to manager when employee's contract has been auto-renewed
        """
        from backend.email_templates import render_contract_auto_renewed_notification

        settings = self.get_email_settings()
        if not settings or not settings.is_active:
            print("Email service not active - skipping contract auto-renewed notification")
            return

        html_body = render_contract_auto_renewed_notification({
            'manager_name_ar': manager_name_ar,
            'manager_name_en': manager_name_en,
            'employee_name_ar': employee_name_ar,
            'employee_name_en': employee_name_en,
            'employee_id': employee_id,
            'new_contract_end_date': new_contract_end_date
        })

        subject = f"Contract Auto-Renewed - Verification Required / تم تجديد العقد تلقائياً - {employee_name_en}"

        # For now, mock the email sending (same as existing send_email method)
        print(f"MOCK EMAIL: To: {manager_email}, Subject: {subject}")
        print(f"Contract auto-renewed notification sent for employee {employee_id}")
        return True 
