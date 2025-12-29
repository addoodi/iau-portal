# Email Notifications Setup - IAU Portal

## Configuration Complete ✓

Email notifications have been successfully configured using **Mailtrap** for testing.

### Mailtrap Credentials
- **Host:** sandbox.smtp.mailtrap.io
- **Port:** 587 (STARTTLS)
- **Username:** 8b19e416e471ec
- **Password:** 6b2fbb4e7b9fec
- **Status:** ✓ Active (SMTP_ENABLED=true)

### What's Configured

1. **Environment Variables** (`.env`)
   - SMTP credentials loaded from .env file
   - Backend loads these on startup via `python-dotenv`

2. **Email Service**
   - Location: `backend/email_service.py`
   - Sends emails when leave requests are created or approved
   - Mock mode is DISABLED (real emails will be sent)

3. **Notification Triggers**
   - **New Leave Request:** Manager receives email when employee submits request
   - **Request Approved:** Employee receives email when manager approves

### How to Use

#### Start the Backend
```bash
cd D:\Code\IAU-Portal\iau-portal
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Test Email Manually
```bash
python backend/test_email.py
```

#### View Emails in Mailtrap
1. Visit: https://mailtrap.io/inboxes
2. Login to your Mailtrap account
3. All test emails will appear in your inbox

### Email Templates

The system sends HTML emails with:
- **Bilingual support** (English/Arabic)
- **Color-coded status** (green for approval, etc.)
- **Leave request details** (dates, duration, type)
- **Professional formatting**

### Email Scenarios

| Event | Recipient | Subject |
|-------|-----------|---------|
| Employee creates leave request | Manager | "New Leave Request / طلب إجازة جديد" |
| Manager approves request | Employee | "Leave Request Approved / تمت الموافقة على طلب الإجازة" |

### Important Notes

1. **Testing Environment:** Mailtrap captures emails without sending to real addresses
2. **Production:** Replace Mailtrap credentials with real SMTP server (Gmail, Office365, etc.)
3. **Security:** Email password is stored in .env file - keep this file secure
4. **Sender Address:** Currently set to `noreply@iau-portal.com`

### Troubleshooting

If emails aren't sending:

1. **Check Backend Logs:**
   ```bash
   tail -f backend/email.log
   ```

2. **Verify Environment Variables:**
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'SMTP Enabled: {os.getenv(\"SMTP_ENABLED\")}')"
   ```

3. **Test Connection:**
   ```bash
   python backend/test_email.py
   ```

4. **Restart Backend:** Environment variables only load on startup

### Next Steps

For production deployment:
1. Replace Mailtrap with production SMTP server
2. Update SMTP_SENDER_EMAIL to real domain
3. Consider using environment-specific .env files
4. Set up email delivery monitoring

---

**Status:** ✓ Ready to use
**Last Updated:** 2025-12-29
