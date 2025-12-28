from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, Response
from typing import List, Optional
import io
import os
from datetime import datetime, timedelta
from hijri_converter import Gregorian

from .models import User, UserCreate, LeaveRequest, Employee, EmployeeWithBalance, EmployeeCreate, LeaveRequestCreate, LeaveRequestUpdate, AdminInit, Unit, EmployeeUpdate, UserPasswordUpdate, UnitCreate, UnitUpdate, AttendanceLog, SignatureUpload, EmailSettings, EmailSettingsCreate, EmailSettingsUpdate, DashboardReportRequest, TeamMemberStats
from .repositories import CSVUserRepository, CSVEmployeeRepository, CSVLeaveRequestRepository
from .services import UserService, EmployeeService, LeaveRequestService, UnitService, AttendanceService, EmailSettingsService, save_attachment
from .document_generator import create_vacation_form, create_dashboard_report
from .auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from .dependencies import get_user_service, get_employee_service, get_leave_request_service, get_unit_service, get_attendance_service, get_email_settings_service
from .calculation import calculate_date_range

app = FastAPI(title="IAU Portal API", version="0.1.0")

# CORS Middleware
# Allow all origins for maximum compatibility in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the IAU Portal API"}

@app.get("/api/health")
def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {"status": "healthy", "service": "iau-portal-api"}

# --- Setup Endpoints ---
@app.get("/api/setup/status")
def setup_status(user_service: UserService = Depends(get_user_service)):
    is_setup = bool(user_service.get_users())
    return {"is_setup": is_setup}

@app.post("/api/setup/initialize", response_model=User, status_code=status.HTTP_201_CREATED)
def initialize_admin(admin_init: AdminInit, user_service: UserService = Depends(get_user_service)):
    if bool(user_service.get_users()):
        raise HTTPException(status_code=400, detail="Application is already set up.")
    try:
        return user_service.initialize_first_user(admin_init)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Authentication Endpoints ---
@app.post("/api/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), user_service: UserService = Depends(get_user_service)):
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_role": user.role}


# --- User Endpoints ---
@app.get("/api/users/me", response_model=EmployeeWithBalance)
def read_users_me(current_user: User = Depends(get_current_user), employee_service: EmployeeService = Depends(get_employee_service)):
    employee = employee_service.get_employee_by_user_id(current_user.id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found for the current user")
    return employee

@app.get("/api/users", response_model=List[User])
def read_users(user_service: UserService = Depends(get_user_service), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view all users")
    return user_service.get_users()

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, 
                user_service: UserService = Depends(get_user_service), 
                current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete users")
    try:
        user_service.delete_user(user_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Employee Endpoints ---
@app.post("/api/employees", response_model=EmployeeWithBalance, status_code=status.HTTP_201_CREATED)
def create_employee_and_user(employee_create: EmployeeCreate, 
                             employee_service: EmployeeService = Depends(get_employee_service),
                             current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create employees")
    try:
        return employee_service.create_user_and_employee(employee_create)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/employees/{employee_id}", response_model=EmployeeWithBalance)
def update_employee(employee_id: str, employee_update: EmployeeUpdate,
                    employee_service: EmployeeService = Depends(get_employee_service),
                    current_user: User = Depends(get_current_user)):

    # Get current user's employee record
    current_employee = employee_service.get_employee_by_user_id(current_user.id)

    # Admin can update any employee, any field
    if current_user.role == "admin":
        try:
            return employee_service.update_employee(employee_id, employee_update)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Manager can only update their direct reports, and only start_date field
    elif current_user.role == "manager":
        target_employee = employee_service.get_employee_by_id(employee_id)

        if not target_employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Verify this is the manager's direct report
        if target_employee.manager_id != current_employee.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this employee")

        # Verify only start_date is being updated
        update_dict = employee_update.dict(exclude_unset=True)
        if set(update_dict.keys()) != {'start_date'}:
            raise HTTPException(
                status_code=403,
                detail="Managers can only update start_date field"
            )

        try:
            return employee_service.update_employee(employee_id, employee_update)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    else:
        raise HTTPException(status_code=403, detail="Not authorized to update employees")

@app.post("/api/users/me/password")
def change_password(password_update: UserPasswordUpdate,
                    user_service: UserService = Depends(get_user_service),
                    current_user: User = Depends(get_current_user)):
    try:
        user_service.change_password(current_user.id, password_update.current_password, password_update.new_password)
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/users/me/signature")
def upload_signature_endpoint(signature_data: SignatureUpload,
                              employee_service: EmployeeService = Depends(get_employee_service),
                              current_user: User = Depends(get_current_user)):
    try:
        path = employee_service.upload_signature(current_user.id, signature_data.image_base64)
        return {"message": "Signature uploaded successfully", "path": path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/users/me/signature")
def delete_signature_endpoint(employee_service: EmployeeService = Depends(get_employee_service),
                              current_user: User = Depends(get_current_user)):
    try:
        employee = employee_service.get_employee_by_user_id(current_user.id)
        if employee and employee.signature_path:
            # Optional: Delete file from disk
            # os.remove(employee.signature_path) 
            employee.signature_path = None
            employee_service.employee_repository.update(employee)
        return {"message": "Signature removed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/employees", response_model=List[EmployeeWithBalance])
def read_employees(employee_service: EmployeeService = Depends(get_employee_service), current_user: User = Depends(get_current_user)):
    return employee_service.get_employees()

@app.get("/api/employees/{employee_id}", response_model=EmployeeWithBalance)
def read_employee(employee_id: str, employee_service: EmployeeService = Depends(get_employee_service), current_user: User = Depends(get_current_user)):
    employee = employee_service.get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

# --- Unit Endpoints ---
@app.get("/api/units", response_model=List[Unit])
def read_units(unit_service: UnitService = Depends(get_unit_service), current_user: User = Depends(get_current_user)):
    return unit_service.get_units()

@app.post("/api/units", response_model=Unit, status_code=status.HTTP_201_CREATED)
def create_unit(unit_create: UnitCreate, 
                unit_service: UnitService = Depends(get_unit_service), 
                current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create units")
    try:
        return unit_service.create_unit(unit_create)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/units/{unit_id}", response_model=Unit)
def update_unit(unit_id: int,
                unit_update: UnitUpdate,
                unit_service: UnitService = Depends(get_unit_service),
                current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update units")
    try:
        return unit_service.update_unit(unit_id, unit_update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_id: int,
    unit_service: UnitService = Depends(get_unit_service),
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: User = Depends(get_current_user)
):
    """Delete a unit if it has no assigned employees"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete units")

    try:
        # Check if unit has any employees
        employees = employee_service.get_employees()
        employees_in_unit = [e for e in employees if e.unit_id == unit_id]

        if employees_in_unit:
            employee_names = ', '.join([f"{e.first_name_en} {e.last_name_en}" for e in employees_in_unit[:3]])
            if len(employees_in_unit) > 3:
                employee_names += f" and {len(employees_in_unit) - 3} more"
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete unit: {len(employees_in_unit)} employee(s) assigned ({employee_names})"
            )

        unit_service.delete_unit(unit_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Leave Request Endpoints ---
@app.get("/api/requests", response_model=List[LeaveRequest])
def read_leave_requests(leave_request_service: LeaveRequestService = Depends(get_leave_request_service), current_user: User = Depends(get_current_user)):
    return leave_request_service.get_leave_requests()

@app.get("/api/requests/{request_id}", response_model=LeaveRequest)
def read_leave_request(request_id: int, leave_request_service: LeaveRequestService = Depends(get_leave_request_service), current_user: User = Depends(get_current_user)):
    leave_request = leave_request_service.get_leave_request_by_id(request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave_request

@app.post("/api/requests", response_model=LeaveRequest, status_code=status.HTTP_201_CREATED)
def create_leave_request(request_in: LeaveRequestCreate, leave_request_service: LeaveRequestService = Depends(get_leave_request_service), current_user: User = Depends(get_current_user)):
    try:
        return leave_request_service.create_leave_request(request_in, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/requests/{request_id}", response_model=LeaveRequest)
def update_leave_request(request_id: int, request_in: LeaveRequestUpdate, 
                         leave_request_service: LeaveRequestService = Depends(get_leave_request_service), 
                         current_user: User = Depends(get_current_user)):
    
    if current_user.role not in ["manager", "admin", "dean"]:
        raise HTTPException(status_code=403, detail="Not authorized to approve/reject requests")

    # TODO: For managers, we should verify that the request belongs to their team.
    # Currently, we trust the role. 
    
    updated_request = leave_request_service.update_leave_request(request_id, request_in)
    if not updated_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return updated_request


@app.get("/api/requests/{request_id}/download")
def download_vacation_form(request_id: int,
                           employee_service: EmployeeService = Depends(get_employee_service),
                           leave_request_service: LeaveRequestService = Depends(get_leave_request_service),
                           current_user: User = Depends(get_current_user)):

    leave_request = leave_request_service.get_leave_request_by_id(request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    # TODO: Add authorization check: is this user allowed to download this form?

    employee = employee_service.get_employee_by_id(leave_request.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    manager = None
    if employee.manager_id:
        manager = employee_service.get_employee_by_id(employee.manager_id)
        print(f"DEBUG: Found Manager: {manager.first_name_en} (ID: {employee.manager_id})")
    else:
        print(f"DEBUG: No manager_id for employee {employee.id}")

    # Date conversion
    def to_hijri_str(date_str: str) -> str:
        if not date_str:
            return ""
        try:
            g_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            h_date = Gregorian(g_date.year, g_date.month, g_date.day).to_hijri()
            return f"{h_date.day}/{h_date.month}/{h_date.year} هـ"
        except (ValueError, TypeError):
            return ""

    # Vacation type translation (case-insensitive)
    vacation_type_map = {
        "annual": "إجازة اعتيادية",
        "sick": "مرضية",
        "unpaid": "بدون أجر",
        "emergency": "طارئة"
    }

    context = {
        'employee_name': f"{employee.first_name_ar} {employee.last_name_ar}",
        'employee_id': employee.id,
        'manager_name': f"{manager.first_name_ar} {manager.last_name_ar}" if manager else "",
        'manager_position': manager.position_ar if manager else "",
        'vacation_type': vacation_type_map.get(leave_request.vacation_type.lower(), leave_request.vacation_type),
        'start_date': to_hijri_str(leave_request.start_date),
        'end_date': to_hijri_str(leave_request.end_date),
        'duration': str(leave_request.duration),
        'balance': str(employee.vacation_balance),
        'current_balance': str(employee.vacation_balance),
        'using_balance': str(leave_request.balance_used),
        'approval_date': to_hijri_str(leave_request.approval_date),
        'approval_x': "x" if leave_request.status == 'Approved' else "",
        'refusal_reason': leave_request.rejection_reason if leave_request.status == 'Rejected' else "",
        'employee_signature_path': employee.signature_path,
        'manager_signature_path': manager.signature_path if manager else None,
    }

    file_stream = create_vacation_form(context)

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=vacation_request_{request_id}.docx"}
    )

# --- Attendance Endpoints ---
@app.get("/api/attendance/today")
def get_today_attendance_status(attendance_service: AttendanceService = Depends(get_attendance_service),
                                current_user: User = Depends(get_current_user)):
    return attendance_service.get_today_status(current_user.id)

@app.post("/api/reports/dashboard")
def download_dashboard_report(
    filter_request: DashboardReportRequest,
    employee_service: EmployeeService = Depends(get_employee_service),
    leave_request_service: LeaveRequestService = Depends(get_leave_request_service),
    unit_service: UnitService = Depends(get_unit_service),
    attendance_service: AttendanceService = Depends(get_attendance_service),
    current_user: User = Depends(get_current_user)
):
    employee = employee_service.get_employee_by_user_id(current_user.id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    unit = None
    if employee.unit_id:
        units = unit_service.get_units()
        unit = next((u for u in units if u.id == employee.unit_id), None)

    # Calculate date range based on filter
    emp_start_date = datetime.strptime(employee.start_date, "%Y-%m-%d").date()
    period_start, period_end = calculate_date_range(
        filter_request.filter_type,
        filter_request.start_date,
        filter_request.end_date,
        emp_start_date
    )

    all_requests = leave_request_service.get_leave_requests()

    # Filter my requests by date range
    my_requests = []
    for r in all_requests:
        if r.employee_id == employee.id:
            req_start = datetime.strptime(r.start_date, "%Y-%m-%d").date()
            req_end = datetime.strptime(r.end_date, "%Y-%m-%d").date()
            # Include if there's any overlap with the period
            if req_start <= period_end and req_end >= period_start:
                my_requests.append(r)

    # Sort requests by date desc
    my_requests.sort(key=lambda x: x.start_date, reverse=True)
    recent_requests = [r.dict() for r in my_requests[:10]]  # Show up to 10 requests in period

    # Balance calc - period specific
    approved_requests_in_period = [r for r in my_requests if r.status == 'Approved']
    used_balance = sum(r.duration for r in approved_requests_in_period)

    # Total balance calculations (not period-specific)
    all_approved = [r for r in all_requests if r.status == 'Approved' and r.employee_id == employee.id]
    total_used = sum(r.duration for r in all_approved)
    earned_balance = round(employee.vacation_balance + total_used, 2)

    attendance_status = attendance_service.get_today_status(current_user.id)

    data = {
        'name_en': f"{employee.first_name_en} {employee.last_name_en}",
        'name_ar': f"{employee.first_name_ar} {employee.last_name_ar}",
        'position_en': employee.position_en,
        'position_ar': employee.position_ar,
        'email': employee.email,
        'unit_en': unit.name_en if unit else "N/A",
        'unit_ar': unit.name_ar if unit else "N/A",
        'balance_available': employee.vacation_balance,
        'balance_used': total_used,
        'balance_earned': earned_balance,
        'contract_end_date': employee.contract_end_date or "N/A",
        'days_remaining': employee.days_remaining_in_contract if employee.days_remaining_in_contract is not None else 0,
        'attendance_status': attendance_status['status'],
        'requests': recent_requests,
        'team_data': [],
        # Period-specific data
        'filter_type': filter_request.filter_type,
        'period_start': period_start.strftime("%Y-%m-%d"),
        'period_end': period_end.strftime("%Y-%m-%d"),
        'period_leaves_taken': used_balance,
        'period_requests_count': len(my_requests),
        # Language and date system preferences
        'language': filter_request.language,
        'date_system': filter_request.date_system
    }

    # Fetch Team Data if Manager/Admin - with period stats
    if current_user.role in ['manager', 'admin', 'dean']:
        all_employees = employee_service.get_employees()
        team_members = []
        for emp in all_employees:
            # Admin/Dean sees all (except self). Manager sees direct reports.
            is_team_member = False
            if current_user.role == 'manager':
                if emp.manager_id == employee.id:
                    is_team_member = True
            elif current_user.role in ['admin', 'dean']:
                if emp.id != employee.id: # Exclude self
                    is_team_member = True

            if is_team_member:
                # Calculate period-specific stats for this member
                member_requests_in_period = []
                for r in all_requests:
                    if r.employee_id == emp.id:
                        req_start = datetime.strptime(r.start_date, "%Y-%m-%d").date()
                        req_end = datetime.strptime(r.end_date, "%Y-%m-%d").date()
                        if req_start <= period_end and req_end >= period_start:
                            member_requests_in_period.append(r)

                approved_in_period = [r for r in member_requests_in_period if r.status == 'Approved']
                total_leaves_taken = sum(r.duration for r in approved_in_period)

                # Calculate leaves by type with details
                leaves_by_type = {}
                leaves_details = []  # List of leave details with dates
                for r in approved_in_period:
                    if r.vacation_type in leaves_by_type:
                        leaves_by_type[r.vacation_type] += r.duration
                    else:
                        leaves_by_type[r.vacation_type] = r.duration

                    # Add detailed leave information
                    leaves_details.append({
                        'type': r.vacation_type,
                        'start_date': r.start_date,
                        'end_date': r.end_date,
                        'duration': r.duration
                    })

                # Check current status - if on leave today
                from datetime import date as dt_date
                today = dt_date.today()
                on_leave_today = False
                for r in all_requests:
                    if r.employee_id == emp.id and r.status == 'Approved':
                        req_start = datetime.strptime(r.start_date, "%Y-%m-%d").date()
                        req_end = datetime.strptime(r.end_date, "%Y-%m-%d").date()
                        if req_start <= today <= req_end:
                            on_leave_today = True
                            break
                current_status = 'On Leave' if on_leave_today else 'Present'

                team_members.append({
                    'name_en': f"{emp.first_name_en} {emp.last_name_en}",
                    'name_ar': f"{emp.first_name_ar} {emp.last_name_ar}",
                    'position_en': emp.position_en,
                    'position_ar': emp.position_ar,
                    'vacation_balance': emp.vacation_balance,
                    'total_leaves_taken': total_leaves_taken,
                    'current_status': current_status,
                    'leaves_by_type': leaves_by_type,
                    'leaves_details': leaves_details
                })
        data['team_data'] = team_members

    file_stream = create_dashboard_report(data)

    # Create filename with date range
    filename = f"dashboard_report_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}.docx"

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# --- Email Settings Endpoints ---
@app.get("/api/email/settings", response_model=Optional[EmailSettings])
def get_email_settings(
    email_settings_service: EmailSettingsService = Depends(get_email_settings_service),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access email settings")
    return email_settings_service.get_email_settings()

@app.post("/api/email/settings", response_model=EmailSettings, status_code=status.HTTP_201_CREATED)
def create_email_settings(
    settings_create: EmailSettingsCreate,
    email_settings_service: EmailSettingsService = Depends(get_email_settings_service),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to configure email settings")
    try:
        return email_settings_service.create_email_settings(settings_create)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/email/settings", response_model=EmailSettings)
def update_email_settings(
    settings_update: EmailSettingsUpdate,
    email_settings_service: EmailSettingsService = Depends(get_email_settings_service),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update email settings")
    try:
        return email_settings_service.update_email_settings(settings_update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/email/test", status_code=status.HTTP_200_OK)
def test_email_settings(
    settings_test: EmailSettingsCreate, # Use create model for plaintext password
    email_settings_service: EmailSettingsService = Depends(get_email_settings_service),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to test email settings")
    try:
        email_settings_service.test_smtp_connection(settings_test)
        return {"message": "SMTP connection test successful!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Attachment Endpoints ---
@app.post("/api/requests/{request_id}/attachments")
async def upload_attachment(
    request_id: int,
    file: UploadFile = File(...),
    leave_request_service: LeaveRequestService = Depends(get_leave_request_service),
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: User = Depends(get_current_user)
):
    leave_request = leave_request_service.get_leave_request_by_id(request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    employee = employee_service.get_employee_by_user_id(current_user.id)
    if not employee or (leave_request.employee_id != employee.id and current_user.role not in ['admin', 'manager', 'dean']):
         raise HTTPException(status_code=403, detail="Not authorized to upload attachments for this request")

    try:
        file_content = await file.read()
        file_path = save_attachment(file_content, file.filename, leave_request.employee_id)
        
        # Update leave request with new attachment
        current_attachments = leave_request.attachments or []
        current_attachments.append(file_path)
        
        leave_request_service.update_leave_request(request_id, LeaveRequestUpdate(attachments=current_attachments))
        
        return {"filename": file.filename, "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/requests/{request_id}/attachments/{filename}")
def download_attachment(
    request_id: int,
    filename: str,
    leave_request_service: LeaveRequestService = Depends(get_leave_request_service),
    employee_service: EmployeeService = Depends(get_employee_service),
    current_user: User = Depends(get_current_user)
):
    leave_request = leave_request_service.get_leave_request_by_id(request_id)
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    # Check authorization (requester or manager/admin)
    employee = employee_service.get_employee_by_user_id(current_user.id)
    
    is_requester = employee and employee.id == leave_request.employee_id
    is_manager = current_user.role in ['manager', 'admin', 'dean']
    
    if not (is_requester or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to view attachments")

    # Construct path securely
    # We need to find the full path in the leave_request.attachments list that ends with this filename
    
    target_path = None
    if leave_request.attachments:
        for path in leave_request.attachments:
            if os.path.basename(path) == filename:
                target_path = path
                break
    
    if not target_path or not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Attachment not found")
        
    return FileResponse(target_path)
