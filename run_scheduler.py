#!/usr/bin/env python3
"""
Run the notification scheduler as a standalone process

This script starts the contract end notification scheduler which runs as a background
service to send automated email notifications to employees about their contract end dates.

Usage:
    python run_scheduler.py

The scheduler will:
- Send 40-day reminders before contract end
- Send critical warnings when vacation balance equals remaining days
- Track sent notifications to avoid duplicates
- Run daily at 8:00 AM
"""

import sys
sys.path.insert(0, '.')

from backend.notification_scheduler import run_scheduler

if __name__ == "__main__":
    print("Starting IAU Portal Notification Scheduler...")
    print("Scheduler will check for contract end notifications daily at 8:00 AM")
    print("Press Ctrl+C to stop")
    run_scheduler()
