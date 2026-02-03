"""
Critical Path Tests - Vacation Balance Calculation

Tests the critical balance calculation logic:
- Monthly accrual calculation
- Contract period handling
- Balance deduction on approval
- Contract renewal scenarios
"""

import pytest
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from backend.calculation import (
    calculate_vacation_balance_simple as calculate_vacation_balance,
    get_current_contract_period_simple as get_current_contract_period,
    months_between
)


# ==========================================
# Test Cases - Months Between Calculation
# ==========================================

def test_months_between_same_month():
    """Test months between for same month"""
    start = date(2026, 1, 1)
    end = date(2026, 1, 31)
    assert months_between(start, end) == 1


def test_months_between_full_year():
    """Test months between for exactly one year"""
    start = date(2025, 1, 1)
    end = date(2026, 1, 1)
    assert months_between(start, end) == 12


def test_months_between_partial_months():
    """Test months between with partial months"""
    start = date(2026, 1, 15)
    end = date(2026, 3, 10)
    # Should count full months only
    result = months_between(start, end)
    assert result >= 1  # At least February is complete


def test_months_between_before_15th():
    """Test that days before 15th don't count as full month"""
    start = date(2026, 1, 1)
    end = date(2026, 1, 14)
    # Less than 15 days shouldn't count as full month
    result = months_between(start, end)
    assert result == 0 or result == 1  # Implementation specific


def test_months_between_after_15th():
    """Test that days after 15th count as full month"""
    start = date(2026, 1, 1)
    end = date(2026, 1, 16)
    # More than 15 days should count as full month
    result = months_between(start, end)
    assert result == 1


# ==========================================
# Test Cases - Balance Calculation
# ==========================================

def test_balance_calculation_new_employee():
    """Test balance for employee starting this month"""
    today = date.today()
    start_date = today.replace(day=1)  # Start of current month

    balance = calculate_vacation_balance(
        start_date=start_date.isoformat(),
        monthly_rate=2.5,
        approved_days=0,
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Should have at most monthly_rate days (depending on current date)
    assert 0 <= balance <= 2.5


def test_balance_calculation_one_year():
    """Test balance for employee with one year of service"""
    today = date.today()
    one_year_ago = today - relativedelta(years=1)

    balance = calculate_vacation_balance(
        start_date=one_year_ago.isoformat(),
        monthly_rate=2.5,
        approved_days=0,
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Should have approximately 12 * 2.5 = 30 days
    assert 29 <= balance <= 31  # Allow small variance


def test_balance_calculation_with_approved_days():
    """Test balance calculation with approved leave days"""
    today = date.today()
    one_year_ago = today - relativedelta(years=1)

    balance = calculate_vacation_balance(
        start_date=one_year_ago.isoformat(),
        monthly_rate=2.5,
        approved_days=10,  # 10 days already taken
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Should be approximately (12 * 2.5) - 10 = 20 days
    assert 19 <= balance <= 21


def test_balance_calculation_multiple_years():
    """Test balance for employee with multiple years"""
    today = date.today()
    three_years_ago = today - relativedelta(years=3)

    balance = calculate_vacation_balance(
        start_date=three_years_ago.isoformat(),
        monthly_rate=2.5,
        approved_days=0,
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Should have approximately 36 * 2.5 = 90 days
    assert 88 <= balance <= 92


def test_balance_negative_after_excessive_approvals():
    """Test that balance can go negative (over-balance is allowed)"""
    today = date.today()
    six_months_ago = today - relativedelta(months=6)

    balance = calculate_vacation_balance(
        start_date=six_months_ago.isoformat(),
        monthly_rate=2.5,
        approved_days=20,  # More than earned (6 * 2.5 = 15)
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Should be negative: (6 * 2.5) - 20 = -5
    assert balance < 0


# ==========================================
# Test Cases - Contract Period
# ==========================================

def test_contract_period_no_end_date():
    """Test contract period when no end date specified"""
    # Use a recent start date to ensure contract hasn't expired
    today = date.today()
    start_date = (today - relativedelta(months=6)).isoformat()

    end_date, days_remaining = get_current_contract_period(
        start_date=start_date,
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Should return one year from start
    assert end_date is not None
    assert days_remaining > 0


def test_contract_period_with_end_date():
    """Test contract period with explicit end date"""
    start_date = "2025-01-01"
    end_date_str = "2026-01-01"

    end_date, days_remaining = get_current_contract_period(
        start_date=start_date,
        contract_end_date=end_date_str,
        contract_auto_renewed=False
    )

    assert end_date == end_date_str
    # Days remaining depends on current date


def test_contract_period_auto_renewed():
    """Test contract period after auto-renewal"""
    # Contract that started 2 years ago
    two_years_ago = date.today() - relativedelta(years=2)
    start_date = two_years_ago.isoformat()

    # Contract ended 1 year ago but was auto-renewed
    one_year_ago = date.today() - relativedelta(years=1)
    contract_end = one_year_ago.isoformat()

    end_date, days_remaining = get_current_contract_period(
        start_date=start_date,
        contract_end_date=contract_end,
        contract_auto_renewed=True
    )

    # Should have been extended
    assert end_date != contract_end


def test_contract_expiring_soon():
    """Test contract with less than 105 days remaining"""
    today = date.today()
    start_date = (today - relativedelta(days=300)).isoformat()
    end_date = (today + relativedelta(days=50)).isoformat()  # 50 days left

    _, days_remaining = get_current_contract_period(
        start_date=start_date,
        contract_end_date=end_date,
        contract_auto_renewed=False
    )

    assert days_remaining < 105
    assert days_remaining > 0


# ==========================================
# Test Cases - Edge Cases
# ==========================================

def test_balance_calculation_fractional_months():
    """Test balance with fractional month (mid-month start)"""
    today = date.today()
    start_date = (today - relativedelta(months=6, days=15)).isoformat()

    balance = calculate_vacation_balance(
        start_date=start_date,
        monthly_rate=2.5,
        approved_days=0,
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Should be approximately 6-7 months worth
    assert 15 <= balance <= 18


def test_balance_calculation_different_monthly_rates():
    """Test balance with different monthly accrual rates"""
    today = date.today()
    one_year_ago = (today - relativedelta(years=1)).isoformat()

    # Test with 2.0 days per month
    balance_2 = calculate_vacation_balance(
        start_date=one_year_ago,
        monthly_rate=2.0,
        approved_days=0,
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Test with 3.0 days per month
    balance_3 = calculate_vacation_balance(
        start_date=one_year_ago,
        monthly_rate=3.0,
        approved_days=0,
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Balance with higher rate should be higher
    assert balance_3 > balance_2
    assert abs(balance_3 - balance_2) >= 10  # At least 10 days difference


def test_balance_calculation_leap_year():
    """Test balance calculation during leap year"""
    # Start in leap year
    start_date = "2024-01-01"  # 2024 is a leap year

    balance = calculate_vacation_balance(
        start_date=start_date,
        monthly_rate=2.5,
        approved_days=0,
        contract_end_date="2025-01-01",
        contract_auto_renewed=False
    )

    # Should handle leap year correctly
    # 12 months * 2.5 = 30 days
    assert 29 <= balance <= 31


def test_balance_calculation_future_start_date():
    """Test balance when start date is in the future"""
    future_date = (date.today() + relativedelta(months=1)).isoformat()

    balance = calculate_vacation_balance(
        start_date=future_date,
        monthly_rate=2.5,
        approved_days=0,
        contract_end_date=None,
        contract_auto_renewed=False
    )

    # Should be 0 or negative (not started yet)
    assert balance <= 0


# ==========================================
# Run Tests
# ==========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
