"""
Contract End Notification Scheduler for IAU Portal
Daily automated job to send vacation balance reminders
"""

import schedule
import time
import logging
from datetime import date, timedelta
from typing import List
import json
from pathlib import Path

from .repositories import CSVEmployeeRepository, CSVUserRepository, CSVLeaveRequestRepository
from .services import EmployeeService
from .email_service import EmailService
from .email_templates import (
    render_contract_reminder_40_days_email,
    render_contract_critical_warning_email
)

# Configure logging
logging.basicConfig(
    filename='backend/notification_scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Tracking file for sent notifications
NOTIFICATIONS_TRACKING_FILE = Path("backend/data/sent_notifications.json")


class NotificationTracker:
    """
    Track which notifications have been sent to avoid duplicates
    """

    def __init__(self):
        self.tracking_data = self._load_tracking_data()

    def _load_tracking_data(self) -> dict:
        """Load tracking data from file"""
        if NOTIFICATIONS_TRACKING_FILE.exists():
            try:
                with open(NOTIFICATIONS_TRACKING_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load tracking data: {e}")
                return {}
        return {}

    def _save_tracking_data(self):
        """Save tracking data to file"""
        try:
            NOTIFICATIONS_TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(NOTIFICATIONS_TRACKING_FILE, 'w') as f:
                json.dump(self.tracking_data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save tracking data: {e}")

    def has_sent(self, employee_id: str, notification_type: str, contract_end_date: str) -> bool:
        """
        Check if notification has been sent

        Args:
            employee_id: Employee ID
            notification_type: '40_days' or 'critical'
            contract_end_date: Contract end date in YYYY-MM-DD format

        Returns:
            bool: True if notification already sent, False otherwise
        """
        key = f"{employee_id}_{notification_type}_{contract_end_date}"
        return key in self.tracking_data

    def mark_sent(self, employee_id: str, notification_type: str, contract_end_date: str):
        """Mark notification as sent"""
        key = f"{employee_id}_{notification_type}_{contract_end_date}"
        self.tracking_data[key] = date.today().isoformat()
        self._save_tracking_data()

    def cleanup_old_entries(self, days_old: int = 400):
        """Remove tracking entries older than specified days"""
        cutoff_date = date.today() - timedelta(days=days_old)
        keys_to_remove = []

        for key, sent_date in self.tracking_data.items():
            try:
                if date.fromisoformat(sent_date) < cutoff_date:
                    keys_to_remove.append(key)
            except:
                keys_to_remove.append(key)  # Remove invalid entries

        for key in keys_to_remove:
            del self.tracking_data[key]

        if keys_to_remove:
            self._save_tracking_data()
            logging.info(f"Cleaned up {len(keys_to_remove)} old tracking entries")


def check_and_send_contract_notifications():
    """
    Daily job to check for contract end dates and send notifications

    Sends two types of notifications:
    1. 40-day reminder: When employee has 40 days left in contract
    2. Critical warning: When vacation balance equals remaining days (±1 day)
    """
    logging.info("Starting contract notification check...")

    try:
        # Initialize services
        employee_repo = CSVEmployeeRepository()
        user_repo = CSVUserRepository()
        leave_request_repo = CSVLeaveRequestRepository()
        employee_service = EmployeeService(employee_repo, user_repo, leave_request_repo)
        email_service = EmailService()
        tracker = NotificationTracker()

        # Get all employees with balance info
        employees = employee_service.get_employees()
        today = date.today()

        notifications_sent = 0

        for employee in employees:
            # Get employee's email from user record
            try:
                employee_user = user_repo.get_by_id(employee.user_id)
                if not employee_user or not employee_user.email:
                    continue

                if not employee.contract_end_date:
                    continue

                contract_end = date.fromisoformat(employee.contract_end_date)
                days_remaining = (contract_end - today).days

                # Skip if contract already ended
                if days_remaining < 0:
                    continue

                # Check for 40-day notification
                if days_remaining == 40:
                    if not tracker.has_sent(employee.id, '40_days', employee.contract_end_date):
                        email_data = {
                            'employee_name_ar': f"{employee.first_name_ar} {employee.last_name_ar}",
                            'employee_name_en': f"{employee.first_name_en} {employee.last_name_en}",
                            'contract_end_date': employee.contract_end_date,
                            'days_remaining': days_remaining,
                            'vacation_balance': employee.vacation_balance
                        }

                        html_body = render_contract_reminder_40_days_email(email_data)
                        success = email_service.send_email(
                            to_email=employee_user.email,
                            subject="Contract End Reminder / تذكير بانتهاء العقد",
                            body=html_body,
                            is_html=True
                        )

                        if success:
                            tracker.mark_sent(employee.id, '40_days', employee.contract_end_date)
                            notifications_sent += 1
                            logging.info(f"40-day notification sent to {employee.id}")

                # Check for critical notification (balance equals remaining days, ±1 day tolerance)
                # This sends when vacation_balance is approximately equal to days_remaining
                balance_equals_days = abs(employee.vacation_balance - days_remaining) <= 1

                if balance_equals_days and days_remaining > 0 and days_remaining <= employee.vacation_balance + 1:
                    if not tracker.has_sent(employee.id, 'critical', employee.contract_end_date):
                        email_data = {
                            'employee_name_ar': f"{employee.first_name_ar} {employee.last_name_ar}",
                            'employee_name_en': f"{employee.first_name_en} {employee.last_name_en}",
                            'contract_end_date': employee.contract_end_date,
                            'days_remaining': days_remaining,
                            'vacation_balance': employee.vacation_balance
                        }

                        html_body = render_contract_critical_warning_email(email_data)
                        success = email_service.send_email(
                            to_email=employee_user.email,
                            subject="CRITICAL: Contract Ending / تحذير حرج: انتهاء العقد",
                            body=html_body,
                            is_html=True
                        )

                        if success:
                            tracker.mark_sent(employee.id, 'critical', employee.contract_end_date)
                            notifications_sent += 1
                            logging.info(f"Critical notification sent to {employee.id}")

            except Exception as e:
                logging.error(f"Error processing employee {employee.id}: {str(e)}")
                continue

        # Cleanup old tracking entries on the 1st of each month
        if today.day == 1:
            tracker.cleanup_old_entries()

        logging.info(f"Contract notification check completed. Sent {notifications_sent} notifications.")

    except Exception as e:
        logging.error(f"Contract notification check failed: {str(e)}")


def run_scheduler():
    """
    Run the scheduler in a continuous loop
    This should be run as a separate process/service
    """
    logging.info("Notification scheduler started")

    # Schedule daily check at 8:00 AM
    schedule.every().day.at("08:00").do(check_and_send_contract_notifications)

    # For testing: also run immediately on startup (comment out in production)
    # check_and_send_contract_notifications()

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    run_scheduler()
