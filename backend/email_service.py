import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

# Configure logging
logging.basicConfig(filename='backend/email.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class EmailService:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587, sender_email=None, sender_password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email or os.getenv("SMTP_USER", "admin@iau-portal.com")
        self.sender_password = sender_password or os.getenv("SMTP_PASSWORD", "mock_password")
        self.mock_mode = True # Default to mock mode for development

    def send_email(self, to_email: str, subject: str, body: str):
        """
        Sends an email. If credentials are not set or mock_mode is True, logs the email instead.
        """
        if self.mock_mode:
            self._log_email(to_email, subject, body)
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()
            logging.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            # Fallback to log
            self._log_email(to_email, subject, body)

    def _log_email(self, to_email, subject, body):
        print(f"--- MOCK EMAIL ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print(f"------------------")
        logging.info(f"Mock email sent to {to_email} | Subject: {subject}")
