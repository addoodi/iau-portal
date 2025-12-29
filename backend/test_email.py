#!/usr/bin/env python3
"""
Test script to verify Mailtrap SMTP configuration
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Mailtrap credentials
SMTP_HOST = "sandbox.smtp.mailtrap.io"
SMTP_PORT = 587
SMTP_USERNAME = "8b19e416e471ec"
SMTP_PASSWORD = "6b2fbb4e7b9fec"
SENDER_EMAIL = "noreply@iau-portal.com"

def test_connection():
    """Test basic SMTP connection"""
    print("Testing SMTP connection to Mailtrap...")
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            print("[OK] Connection successful!")
            return True
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        return False

def send_test_email(recipient="test@example.com"):
    """Send a test email"""
    print(f"\nSending test email to {recipient}...")
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "IAU Portal - Email Test"
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient

        # Email body
        html_body = """
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #0f5132;">IAU Portal Email Test</h2>
                <p>This is a test email from the IAU Portal system.</p>
                <p>If you're seeing this in Mailtrap, email notifications are working correctly!</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Sent from IAU Portal Electronic Services
                </p>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())

        print(f"[OK] Test email sent successfully!")
        print(f"  Check your Mailtrap inbox at: https://mailtrap.io/inboxes")
        return True

    except Exception as e:
        print(f"[FAIL] Failed to send email: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("IAU Portal - Mailtrap Email Configuration Test")
    print("=" * 60)

    # Test 1: Connection
    if test_connection():
        # Test 2: Send test email
        send_test_email("admin@iau-portal.test")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
