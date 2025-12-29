"""
Manager hierarchy utilities for recursive subordinate lookups.

This module provides functions to traverse the employee management hierarchy
and find all subordinates (direct and indirect) of a given manager.
"""

from typing import List, Set
from backend.models import EmployeeWithBalance


def get_all_subordinates(
    manager_id: str,
    all_employees: List[EmployeeWithBalance],
    include_indirect: bool = True
) -> List[str]:
    """
    Get all subordinate employee IDs for a manager (direct and indirect).

    Args:
        manager_id: The manager's employee ID
        all_employees: List of all employees in the system
        include_indirect: If True, includes subordinates of subordinates (recursive)

    Returns:
        List of employee IDs that report to this manager (directly or indirectly)

    Example:
        >>> # Manager1 -> Manager2 -> Employee
        >>> subordinates = get_all_subordinates(manager1_id, all_employees, True)
        >>> # Returns [manager2_id, employee_id]
    """
    subordinate_ids: Set[str] = set()
    visited: Set[str] = set()  # Prevent infinite loops from circular references

    def find_subordinates(mgr_id: str):
        # Prevent infinite recursion from circular references
        if mgr_id in visited:
            return
        visited.add(mgr_id)

        # Find direct reports
        direct_reports = [emp for emp in all_employees if emp.manager_id == mgr_id]

        for employee in direct_reports:
            # Skip if this would create a circular reference
            if employee.id == mgr_id:
                continue

            subordinate_ids.add(employee.id)

            # Recursively find their subordinates if include_indirect is True
            if include_indirect:
                find_subordinates(employee.id)

    find_subordinates(manager_id)
    return list(subordinate_ids)


def is_subordinate_of(
    employee_id: str,
    manager_id: str,
    all_employees: List[EmployeeWithBalance]
) -> bool:
    """
    Check if an employee is a subordinate (direct or indirect) of a manager.

    Args:
        employee_id: The employee to check
        manager_id: The manager to check against
        all_employees: List of all employees

    Returns:
        True if employee is a subordinate of manager (directly or indirectly)

    Example:
        >>> # Manager1 -> Manager2 -> Employee
        >>> is_subordinate_of(employee_id, manager1_id, all_employees)
        >>> # Returns True
    """
    subordinates = get_all_subordinates(manager_id, all_employees, include_indirect=True)
    return employee_id in subordinates
