from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional
from .models import Employee, LeaveRequest

def get_current_contract_period(start_date: date, today: date) -> Tuple[date, date]:
    """
    Returns the start and end date of the current 11-month contract period.
    """
    contract_duration_months = 11
    
    if today < start_date:
        return start_date, start_date + relativedelta(months=contract_duration_months)

    current_start = start_date
    # Calculate the number of full periods passed
    # (today.year - start.year) * 12 + (today.month - start.month) ... roughly
    # Easier to just jump by 11 months until we pass today, then step back one?
    # Or just iterative if duration is short.
    
    # Optimization: Calculate approximate jumps
    months_diff = (today.year - start_date.year) * 12 + (today.month - start_date.month)
    periods_passed = months_diff // contract_duration_months
    
    # Estimate start
    estimated_start = start_date + relativedelta(months=periods_passed * contract_duration_months)
    
    # Adjust if needed
    current_start = estimated_start
    while True:
        current_end = current_start + relativedelta(months=contract_duration_months)
        if current_start <= today < current_end:
            return current_start, current_end
        
        if today < current_start:
             # We went too far (shouldn't happen with the logic above but safety)
             current_start -= relativedelta(months=contract_duration_months)
        else:
             current_start = current_end

def calculate_vacation_balance(employee: Employee, all_approved_requests: List[LeaveRequest]) -> float:
    """
    Calculates the current vacation balance based on the CURRENT 11-month contract period.
    Balances from previous contracts are lost (reset to 0).
    """
    emp_start_date = datetime.strptime(employee.start_date, "%Y-%m-%d").date()
    today = date.today()

    if emp_start_date > today:
        return 0.0

    # 1. Determine Current Contract Period
    contract_start, contract_end = get_current_contract_period(emp_start_date, today)

    # 2. Calculate Earned Balance for CURRENT period only
    # We treat calculation as if the employee started on `contract_start`
    # But we must preserve the original "day of month" logic for the 15th cutoff.
    # The original logic used `start_date.day`. We should use `contract_start.day`? 
    # Since `contract_start` is derived from `start_date` via `relativedelta`, the day component is preserved (unless Feb 29 etc).
    
    effective_start_date = contract_start
    
    earned_balance = 0.0
    
    # Iterate months starting from the month of effective_start_date
    current_month_cursor = date(effective_start_date.year, effective_start_date.month, 1)
    # Align cursor to the 1st of the month
    
    while current_month_cursor <= today:
        # Month of contract start
        if current_month_cursor.year == effective_start_date.year and current_month_cursor.month == effective_start_date.month:
            if effective_start_date.day <= 15:
                earned_balance += employee.monthly_vacation_earned
            else:
                earned_balance += employee.monthly_vacation_earned / 2.0
        
        # Current month (today's month)
        elif current_month_cursor.year == today.year and current_month_cursor.month == today.month:
             if today.day > 15:
                earned_balance += employee.monthly_vacation_earned
             else:
                earned_balance += employee.monthly_vacation_earned / 2.0

        # Full months in between
        else:
            earned_balance += employee.monthly_vacation_earned

        # Move to the next month
        current_month_cursor += relativedelta(months=1)

    # --- Calculate Used Vacation ---
    # Only count requests that fall within the current contract period
    employee_requests = [req for req in all_approved_requests if req.employee_id == employee.id]
    
    total_used = 0
    for req in employee_requests:
        req_start = datetime.strptime(req.start_date, "%Y-%m-%d").date()
        # If request starts after (or on) the current contract start, deduct it.
        # Assumption: You can't start a vacation in previous contract and end in current (logic would be complex).
        # We simplify: Deduct based on start date.
        if req_start >= contract_start:
            total_used += req.duration

    return round(max(0.0, earned_balance - total_used), 2)

def calculate_date_range(filter_type: str, start_date_str: Optional[str] = None,
                        end_date_str: Optional[str] = None,
                        contract_start: Optional[date] = None) -> Tuple[date, date]:
    """
    Calculate date range based on filter type.

    Args:
        filter_type: One of 'ytd', 'last_30', 'last_60', 'last_90', 'full_year', 'custom'
        start_date_str: Custom start date (YYYY-MM-DD) for 'custom' filter
        end_date_str: Custom end date (YYYY-MM-DD) for 'custom' filter
        contract_start: Employee contract start date for 'full_year' filter

    Returns:
        Tuple of (start_date, end_date)
    """
    today = date.today()

    if filter_type == 'ytd':
        # Year to date: Jan 1 to today
        return date(today.year, 1, 1), today

    elif filter_type == 'last_30':
        return today - timedelta(days=30), today

    elif filter_type == 'last_60':
        return today - timedelta(days=60), today

    elif filter_type == 'last_90':
        return today - timedelta(days=90), today

    elif filter_type == 'full_year':
        # Full contract year (11 months)
        if contract_start:
            contract_period_start, contract_period_end = get_current_contract_period(contract_start, today)
            return contract_period_start, contract_period_end
        else:
            # Fallback to calendar year if no contract start provided
            return date(today.year, 1, 1), today

    elif filter_type == 'custom':
        if start_date_str and end_date_str:
            start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            return start, end
        else:
            # Fallback to last 30 days if custom dates not provided
            return today - timedelta(days=30), today

    else:
        # Default to last 30 days
        return today - timedelta(days=30), today
