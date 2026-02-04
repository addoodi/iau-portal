"""
Tests for permanent employee vacation balance calculation.

Tests the calendar year period, carry-over logic, and balance calculation
for permanent employees (as opposed to contractors with 11-month rolling periods).
"""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test_iau_portal.db"
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

import pytest
from datetime import date
from unittest.mock import patch
from backend.models import Employee, LeaveRequest
from backend.calculation import (
    calculate_permanent_vacation_balance,
    get_permanent_contract_period,
    _calculate_earned_for_year,
    _calculate_used_for_year,
)


def _make_employee(start_date="2024-01-01", monthly_rate=2.5, emp_id="EMP-001"):
    return Employee(
        id=emp_id,
        user_id="00000000-0000-0000-0000-000000000001",
        first_name_ar="test",
        last_name_ar="test",
        first_name_en="Test",
        last_name_en="User",
        position_ar="موظف",
        position_en="Employee",
        unit_id=1,
        start_date=start_date,
        monthly_vacation_earned=monthly_rate,
        employee_type="permanent",
    )


def _make_request(emp_id, start_date, end_date, duration, status="Approved"):
    return LeaveRequest(
        id=1,
        employee_id=emp_id,
        vacation_type="Annual",
        start_date=start_date,
        end_date=end_date,
        duration=duration,
        status=status,
        balance_used=duration,
    )


class TestGetPermanentContractPeriod:
    def test_returns_jan1_to_dec31(self):
        period_start, period_end = get_permanent_contract_period(date(2026, 6, 15))
        assert period_start == date(2026, 1, 1)
        assert period_end == date(2026, 12, 31)

    def test_jan1_returns_current_year(self):
        period_start, period_end = get_permanent_contract_period(date(2026, 1, 1))
        assert period_start == date(2026, 1, 1)
        assert period_end == date(2026, 12, 31)

    def test_dec31_returns_current_year(self):
        period_start, period_end = get_permanent_contract_period(date(2026, 12, 31))
        assert period_start == date(2026, 1, 1)
        assert period_end == date(2026, 12, 31)


class TestEarnedForYear:
    @patch("backend.calculation.date")
    def test_full_year_earns_30_days(self, mock_date):
        """Employee working full year at 2.5/month earns 30 days (12 months * 2.5)"""
        mock_date.today.return_value = date(2026, 12, 31)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

        emp = _make_employee(start_date="2024-01-01")
        earned = _calculate_earned_for_year(
            emp,
            year_start=date(2026, 1, 1),
            year_end=date(2026, 12, 31),
            emp_start_date=date(2024, 1, 1),
            calc_end=date(2026, 12, 31),
        )
        assert earned == 30.0  # 12 months * 2.5

    def test_mid_year_start(self):
        """Employee starting July 1 earns for 6 months only"""
        emp = _make_employee(start_date="2026-07-01")
        earned = _calculate_earned_for_year(
            emp,
            year_start=date(2026, 1, 1),
            year_end=date(2026, 12, 31),
            emp_start_date=date(2026, 7, 1),
            calc_end=date(2026, 12, 31),
        )
        assert earned == 15.0  # 6 months * 2.5

    def test_partial_month_start(self):
        """Employee starting after 15th gets half rate for first month"""
        emp = _make_employee(start_date="2026-07-20")
        earned = _calculate_earned_for_year(
            emp,
            year_start=date(2026, 1, 1),
            year_end=date(2026, 12, 31),
            emp_start_date=date(2026, 7, 20),
            calc_end=date(2026, 12, 31),
        )
        # July (half: 1.25) + Aug-Dec (5 months * 2.5 = 12.5) = 13.75
        assert earned == 13.75

    def test_zero_earned_if_not_started(self):
        """Employee hasn't started yet earns nothing"""
        emp = _make_employee(start_date="2027-01-01")
        earned = _calculate_earned_for_year(
            emp,
            year_start=date(2026, 1, 1),
            year_end=date(2026, 12, 31),
            emp_start_date=date(2027, 1, 1),
            calc_end=date(2026, 12, 31),
        )
        assert earned == 0.0


class TestUsedForYear:
    def test_counts_approved_requests_in_year(self):
        requests = [
            _make_request("EMP-001", "2026-03-01", "2026-03-05", 5),
            _make_request("EMP-001", "2026-06-10", "2026-06-15", 5),
        ]
        used = _calculate_used_for_year(
            "EMP-001", requests, date(2026, 1, 1), date(2026, 12, 31)
        )
        assert used == 10

    def test_excludes_previous_year_requests(self):
        requests = [
            _make_request("EMP-001", "2025-11-01", "2025-11-05", 5),
            _make_request("EMP-001", "2026-03-01", "2026-03-05", 5),
        ]
        used = _calculate_used_for_year(
            "EMP-001", requests, date(2026, 1, 1), date(2026, 12, 31)
        )
        assert used == 5

    def test_excludes_other_employees(self):
        requests = [
            _make_request("EMP-001", "2026-03-01", "2026-03-05", 5),
            _make_request("EMP-002", "2026-03-01", "2026-03-05", 5),
        ]
        used = _calculate_used_for_year(
            "EMP-001", requests, date(2026, 1, 1), date(2026, 12, 31)
        )
        assert used == 5


class TestCalculatePermanentVacationBalance:
    @patch("backend.calculation.date")
    def test_basic_balance_no_carry_over(self, mock_date):
        """First-year employee, no carry-over (started this year)"""
        mock_date.today.return_value = date(2026, 6, 16)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

        emp = _make_employee(start_date="2026-01-01")
        balance, carry_over = calculate_permanent_vacation_balance(emp, [], 15)

        # Jan-Jun (6 months * 2.5 = 15.0), no carry-over (started this year)
        assert balance == 15.0
        assert carry_over == 0.0

    @patch("backend.calculation.date")
    def test_carry_over_from_previous_year(self, mock_date):
        """Employee with unused balance from previous year gets carry-over"""
        mock_date.today.return_value = date(2026, 2, 16)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

        emp = _make_employee(start_date="2024-01-01")
        # Previous year: earned 30 (12 months * 2.5), used 20 -> 10 remaining
        prev_year_requests = [
            _make_request("EMP-001", "2025-03-01", "2025-03-11", 10),
            _make_request("EMP-001", "2025-08-01", "2025-08-11", 10),
        ]
        balance, carry_over = calculate_permanent_vacation_balance(
            emp, prev_year_requests, 15
        )

        # Carry-over: min(10, 15) = 10
        assert carry_over == 10.0
        # This year: Jan-Feb (2 months * 2.5 = 5.0) + carry_over (10) = 15.0
        assert balance == 15.0

    @patch("backend.calculation.date")
    def test_carry_over_capped_at_max(self, mock_date):
        """Carry-over should not exceed max_carry_over_days"""
        mock_date.today.return_value = date(2026, 2, 16)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

        emp = _make_employee(start_date="2024-01-01")
        # Previous year: earned 30, used 0 -> 30 remaining, but capped at 15
        balance, carry_over = calculate_permanent_vacation_balance(emp, [], 15)

        assert carry_over == 15.0  # Capped at max
        # This year: 2 months * 2.5 = 5.0 + carry_over 15 = 20.0
        assert balance == 20.0

    @patch("backend.calculation.date")
    def test_zero_carry_over_when_all_used(self, mock_date):
        """No carry-over when all previous year balance was used"""
        mock_date.today.return_value = date(2026, 2, 16)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

        emp = _make_employee(start_date="2024-01-01")
        # Previous year: earned 30, used 30
        prev_requests = [
            _make_request("EMP-001", "2025-01-15", "2025-02-14", 30),
        ]
        balance, carry_over = calculate_permanent_vacation_balance(
            emp, prev_requests, 15
        )

        assert carry_over == 0.0
        # This year: 2 months * 2.5 = 5.0
        assert balance == 5.0

    @patch("backend.calculation.date")
    def test_balance_with_current_year_usage(self, mock_date):
        """Balance deducted for current year approved requests"""
        mock_date.today.return_value = date(2026, 6, 16)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

        emp = _make_employee(start_date="2024-01-01")
        requests = [
            _make_request("EMP-001", "2026-03-01", "2026-03-06", 5),
        ]
        balance, carry_over = calculate_permanent_vacation_balance(
            emp, requests, 15
        )

        # Carry-over: min(30, 15) = 15
        assert carry_over == 15.0
        # This year earned: 6 months * 2.5 = 15.0
        # Total: 15 + 15 - 5 = 25.0
        assert balance == 25.0

    @patch("backend.calculation.date")
    def test_future_start_date_returns_zero(self, mock_date):
        """Employee who hasn't started yet has zero balance"""
        mock_date.today.return_value = date(2026, 6, 16)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

        emp = _make_employee(start_date="2027-01-01")
        balance, carry_over = calculate_permanent_vacation_balance(emp, [], 15)

        assert balance == 0.0
        assert carry_over == 0.0
