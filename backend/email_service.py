import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

# Configure logging with UTF-8 encoding to support Arabic characters
logging.basicConfig(filename='backend/email.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    encoding='utf-8')

class EmailService:
    def __init__(self):
        """
        Initialize email service with configuration from environment variables.
        """
        # Load configuration from environment variables
        self.smtp_server = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.sender_email = os.getenv("SMTP_SENDER_EMAIL", "noreply@iau-portal.com")
        self.sender_password = os.getenv("SMTP_PASSWORD", "")

        # Mock mode is controlled by SMTP_ENABLED environment variable
        smtp_enabled = os.getenv("SMTP_ENABLED", "false").lower()
        self.mock_mode = smtp_enabled != "true"

        if self.mock_mode:
            logging.info("Email service initialized in MOCK MODE (SMTP_ENABLED=false)")
        else:
            logging.info(f"Email service initialized for {self.smtp_server}:{self.smtp_port}")

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False):
        """
        Sends an email. If mock_mode is True, logs the email instead of sending.

        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            body (str): Email body content (plain text or HTML)
            is_html (bool): If True, body is treated as HTML; if False, plain text

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if self.mock_mode:
            self._log_email(to_email, subject, body)
            return True

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach body based on type
            if is_html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.sender_password)
            server.sendmail(self.sender_email, to_email, msg.as_string())
            server.quit()

            logging.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            # Fallback to log
            self._log_email(to_email, subject, body)
            return False

    def _log_email(self, to_email, subject, body):
        print(f"--- MOCK EMAIL ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print(f"------------------")
        logging.info(f"Mock email sent to {to_email} | Subject: {subject}")
