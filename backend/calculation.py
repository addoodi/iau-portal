from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple, Optional, Union
from .models import Employee, LeaveRequest


def months_between(start: date, end: date) -> int:
    """
    Calculate the number of full months between two dates.
    Follows the 15th day rule: working past the 15th counts as a full month.

    Examples:
        - Jan 1 to Jan 31 = 1 month (full month)
        - Jan 1 to Jan 16 = 1 month (passed 15th)
        - Jan 1 to Jan 14 = 0 months (didn't reach 15th)
        - Jan 1, 2025 to Jan 1, 2026 = 12 months
        - Jan 1 to Dec 31 = 12 months
    """
    if start > end:
        return 0

    # Calculate month difference
    months_diff = (end.year - start.year) * 12 + (end.month - start.month)

    # Same month: check if we passed 15th
    if months_diff == 0:
        return 1 if end.day > 15 else 0

    # Different months: start with the number of complete months between
    # (not including start and end months)
    count = max(0, months_diff - 1)

    # Add start month if we started on or before the 15th
    if start.day <= 15:
        count += 1

    # Add end month if we ended after the 15th
    if end.day > 15:
        count += 1

    return count

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


def get_permanent_contract_period(today: date) -> Tuple[date, date]:
    """
    Returns the current calendar year period for permanent employees.
    Period is always Jan 1 to Dec 31 of the current year.
    """
    return date(today.year, 1, 1), date(today.year, 12, 31)


def _calculate_earned_for_year(employee: Employee, year_start: date, year_end: date,
                                emp_start_date: date, calc_end: date) -> float:
    """
    Calculate earned vacation balance for a given year period.
    Handles the case where employee started mid-year.
    """
    # Effective start is the later of year_start or employee start date
    effective_start = max(year_start, emp_start_date)
    # Effective end is the earlier of year_end or calc_end
    effective_end = min(year_end, calc_end)

    if effective_start > effective_end:
        return 0.0

    earned = 0.0
    current_month_cursor = date(effective_start.year, effective_start.month, 1)

    while current_month_cursor <= effective_end:
        # Month of effective start
        if (current_month_cursor.year == effective_start.year and
                current_month_cursor.month == effective_start.month):
            if effective_start.day <= 15:
                earned += employee.monthly_vacation_earned
            else:
                earned += employee.monthly_vacation_earned / 2.0

        # Month of effective end (if different from start month)
        elif (current_month_cursor.year == effective_end.year and
              current_month_cursor.month == effective_end.month):
            if effective_end.day > 15:
                earned += employee.monthly_vacation_earned
            else:
                earned += employee.monthly_vacation_earned / 2.0

        # Full months in between
        else:
            earned += employee.monthly_vacation_earned

        current_month_cursor += relativedelta(months=1)

    return earned


def _calculate_used_for_year(employee_id: str, all_approved_requests: List[LeaveRequest],
                              year_start: date, year_end: date) -> int:
    """Calculate total approved leave days used within a year period."""
    total_used = 0
    for req in all_approved_requests:
        if req.employee_id != employee_id:
            continue
        req_start = datetime.strptime(req.start_date, "%Y-%m-%d").date()
        if year_start <= req_start <= year_end:
            total_used += req.duration
    return total_used


def calculate_permanent_vacation_balance(
    employee: Employee,
    all_approved_requests: List[LeaveRequest],
    max_carry_over_days: int = 15
) -> Tuple[float, float]:
    """
    Calculates vacation balance for permanent employees.
    Period is calendar year (Jan 1 - Dec 31).
    Unused balance from the previous year carries over, capped at max_carry_over_days.

    Returns:
        Tuple of (total_balance, carry_over_amount)
    """
    emp_start_date = datetime.strptime(employee.start_date, "%Y-%m-%d").date()
    today = date.today()

    if emp_start_date > today:
        return 0.0, 0.0

    # Current year period
    current_year_start = date(today.year, 1, 1)
    current_year_end = date(today.year, 12, 31)

    # Calculate carry-over from previous year (one-year lookback, non-recursive)
    carry_over = 0.0
    prev_year_start = date(today.year - 1, 1, 1)
    prev_year_end = date(today.year - 1, 12, 31)

    if emp_start_date <= prev_year_end:
        prev_earned = _calculate_earned_for_year(
            employee, prev_year_start, prev_year_end, emp_start_date, prev_year_end
        )
        prev_used = _calculate_used_for_year(
            employee.id, all_approved_requests, prev_year_start, prev_year_end
        )
        prev_remaining = max(0.0, prev_earned - prev_used)
        carry_over = min(prev_remaining, max_carry_over_days)

    # Calculate earned for current year
    earned_this_year = _calculate_earned_for_year(
        employee, current_year_start, current_year_end, emp_start_date, today
    )

    # Calculate used for current year
    used_this_year = _calculate_used_for_year(
        employee.id, all_approved_requests, current_year_start, current_year_end
    )

    total_balance = carry_over + earned_this_year - used_this_year
    return round(max(0.0, total_balance), 2), round(carry_over, 2)


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


# ============================================
# Simplified Test API (for pytest tests)
# ============================================

def calculate_vacation_balance_simple(
    start_date: str,
    monthly_rate: float,
    approved_days: int,
    contract_end_date: Optional[str] = None,
    contract_auto_renewed: bool = False
) -> float:
    """
    Simplified API for calculating vacation balance (used by tests).

    Args:
        start_date: Employee start date (YYYY-MM-DD)
        monthly_rate: Monthly vacation accrual rate
        approved_days: Total approved vacation days
        contract_end_date: Contract end date (YYYY-MM-DD) or None
        contract_auto_renewed: Whether contract auto-renews

    Returns:
        Current vacation balance
    """
    emp_start = datetime.strptime(start_date, "%Y-%m-%d").date()
    today = date.today()

    if emp_start > today:
        return 0.0

    # Determine calculation end date
    calc_end_date = today
    if contract_end_date:
        contract_end = datetime.strptime(contract_end_date, "%Y-%m-%d").date()
        # Use the earlier of today or contract end
        calc_end_date = min(today, contract_end)

    # Calculate months worked
    months_worked = months_between(emp_start, calc_end_date)

    # Calculate earned balance
    earned = months_worked * monthly_rate

    # Deduct approved days
    balance = earned - approved_days

    return round(balance, 2)


def get_current_contract_period_simple(
    start_date: str,
    contract_end_date: Optional[str] = None,
    contract_auto_renewed: bool = False
) -> Tuple[str, int]:
    """
    Simplified API for getting contract period info (used by tests).

    Args:
        start_date: Employee start date (YYYY-MM-DD)
        contract_end_date: Contract end date (YYYY-MM-DD) or None
        contract_auto_renewed: Whether contract auto-renews

    Returns:
        Tuple of (end_date_str, days_remaining)
    """
    emp_start = datetime.strptime(start_date, "%Y-%m-%d").date()
    today = date.today()

    # Default contract end (1 year from start)
    if contract_end_date:
        end_date = datetime.strptime(contract_end_date, "%Y-%m-%d").date()

        # If auto-renewed and past end date, extend by 1 year
        if contract_auto_renewed and today > end_date:
            end_date = end_date + relativedelta(years=1)
    else:
        # Default to 1 year from start
        end_date = emp_start + relativedelta(years=1)

    # Calculate days remaining
    if end_date > today:
        days_remaining = (end_date - today).days
    else:
        days_remaining = 0

    return end_date.isoformat(), days_remaining
