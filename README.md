# IAU Portal - Electronic Services Portal

A comprehensive web-based employee management system for the Institute of Innovation and Entrepreneurship. The portal streamlines leave request management, attendance tracking, and administrative workflows with full bilingual support (English/Arabic).

## 🌟 Features

### Employee Self-Service
- **Leave Request Management**: Submit and track vacation requests (annual, sick, emergency)
- **Vacation Balance Tracking**: Real-time vacation balance with earned/used/available breakdown
- **Digital Signatures**: Upload and manage digital signatures for automated document signing
- **Personal Dashboard**: View contract status, upcoming expirations, and attendance record
- **Bilingual Interface**: Full support for English and Arabic with RTL layout

### Manager Features
- **Team Timeline View**: 60-day scrollable calendar showing team availability
- **Approval Workflow**: Review and approve/reject leave requests with conflict detection
- **Employee Detail View**: View team member vacation balances and contract dates
- **Contract Date Management**: Update employee contract start dates with automatic recalculation
- **Team Status Indicators**: Visual highlighting of team members on leave vs. present

### Admin Features
- **User Management**: Create and manage user accounts with role-based access
- **Unit Management**: Organize employees into departments/units with delete protection
- **Email Configuration**: Configure SMTP settings for automated notifications
- **System Settings**: Manage site-wide configuration and preferences
- **Dashboard Reports**: Generate comprehensive reports with multiple time period filters

### Automated Notifications
- **Contract Expiration Reminders**: 40-day advance notice before contract end
- **Critical Warnings**: Alerts when vacation balance equals remaining contract days
- **Daily Scheduler**: Automated email notifications at 8:00 AM
- **Duplicate Prevention**: Smart tracking to avoid sending duplicate notifications

### Calendar System
- **Dual Calendar Support**: Gregorian and Hijri calendar systems
- **Interactive Timeline**: Visual representation of team availability
- **Conflict Detection**: Automatic detection of overlapping leave requests
- **Color-Coded Status**: Easy identification of approved, pending, and rejected requests

## 🛠️ Tech Stack

### Frontend
- **React 19.2** - Modern UI framework
- **React Router v7** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast build tool and dev server
- **Lucide React** - Icon library

### Backend
- **FastAPI** - High-performance Python web framework
- **Pydantic** - Data validation and settings management
- **ReportLab** - PDF document generation
- **Python Email** - SMTP email service
- **Schedule** - Task scheduling for automated jobs

### Infrastructure
- **Docker & Docker Compose** - Containerized deployment
- **Nginx** - Reverse proxy and static file serving
- **PostgreSQL 16 Alpine** - Production database with ACID guarantees

## 📋 Prerequisites

- **Node.js** 18+ and npm (for local development)
- **Python** 3.11+ (for local development)
- **Docker & Docker Compose** (for production deployment)

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended for Production)

1. **Clone the repository**
```bash
git clone https://github.com/addoodi/iau-portal.git
cd iau-portal
```

2. **Create data directories**
```bash
mkdir -p /home/addoodi/appdata/iau-portal/data
mkdir -p /home/addoodi/appdata/iau-portal/templates
```

3. **Configure environment** (optional)
```bash
cp .env.example .env
# Edit .env to customize port (default: 3000)
```

4. **Start the application**
```bash
docker-compose up -d
```

5. **Access the portal**
- Open your browser to `http://localhost:3000`
- First-time setup will prompt you to create an admin account

6. **View logs**
```bash
docker-compose logs -f
```

7. **Stop the application**
```bash
docker-compose down
```

### Option 2: Local Development

#### Backend Setup
```bash
# Navigate to project root
cd iau-portal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn backend.main:app --reload --port 8000
```

#### Frontend Setup
```bash
# In a new terminal, navigate to project root
cd iau-portal

# Install dependencies
npm install

# Start development server
npm start
```

The application will be available at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Frontend Port (Docker deployment)
FRONTEND_PORT=3000

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://iau_admin:iau_secure_password_2024@localhost:5432/iau_portal
POSTGRES_USER=iau_admin
POSTGRES_PASSWORD=iau_secure_password_2024
POSTGRES_DB=iau_portal

# Email Configuration (optional - can be set via UI)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=noreply@example.com
```

### Email Setup

1. Navigate to **Site Settings** → **Email Settings**
2. Configure SMTP server details
3. Test connection
4. Save settings

For Gmail:
- Enable 2-factor authentication
- Generate an [App Password](https://support.google.com/accounts/answer/185833)
- Use the app password in SMTP_PASSWORD

### Notification Scheduler

To run automated contract expiration notifications:

```bash
python run_scheduler.py
```

Or run as a background service:
```bash
nohup python run_scheduler.py > scheduler.log 2>&1 &
```

## 📁 Project Structure

```
iau-portal/
├── backend/
│   ├── data/              # User uploads & attachments
│   │   ├── signatures/    # Employee signature images
│   │   ├── attachments/   # Leave request attachments
│   │   └── sent_notifications.json
│   ├── templates/         # Document templates
│   ├── database.py        # SQLAlchemy models & DB setup
│   ├── db_repositories.py # PostgreSQL data access layer
│   ├── email_templates.py # Email HTML templates
│   ├── notification_scheduler.py
│   ├── main.py           # FastAPI application
│   ├── models.py         # Pydantic models
│   ├── services.py       # Business logic
│   └── auth.py           # Authentication
├── src/
│   ├── components/       # React components
│   ├── pages/           # Page components
│   ├── context/         # React context (state)
│   ├── utils/           # Utilities and translations
│   └── api.js           # API client
├── public/              # Static assets
├── docker-compose.yml   # Docker orchestration
├── Dockerfile.backend   # Backend container
├── Dockerfile.frontend  # Frontend container
└── nginx.conf          # Nginx configuration
```

## 👥 User Roles

### Employee
- Submit leave requests
- View personal vacation balance
- Track request status
- Upload digital signature
- Change password

### Manager
- All employee features
- Approve/reject team leave requests
- View team timeline and availability
- Update team member contract dates
- Conflict detection for team requests

### Admin
- All manager features
- Create and manage users
- Manage organizational units
- Configure email settings
- Access all leave requests
- Generate system reports

## 🔐 Security

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password encryption
- **Role-Based Access Control**: Granular permission system
- **HTTPS Ready**: Nginx reverse proxy supports SSL/TLS
- **Input Validation**: Pydantic schema validation

## 📊 Data Persistence

The application uses **PostgreSQL 16 Alpine** for production-grade data storage with ACID transaction guarantees.

### Database Schema
- **users** - User accounts and authentication (UUID primary keys)
- **employees** - Employee profiles and contracts
- **units** - Organizational units/departments
- **leave_requests** - Vacation request records with JSON attachments
- **attendance_logs** - Daily check-in/check-out records
- **email_settings** - SMTP configuration (singleton table)

### Database Backup

**Automated PostgreSQL Backup:**
```bash
# Backup database to SQL file
docker exec iau-portal-postgres pg_dump -U iau_admin iau_portal > backup-$(date +%Y%m%d).sql

# Backup with gzip compression
docker exec iau-portal-postgres pg_dump -U iau_admin iau_portal | gzip > backup-$(date +%Y%m%d).sql.gz
```

**Database Restore:**
```bash
# Restore from SQL file
docker exec -i iau-portal-postgres psql -U iau_admin iau_portal < backup-20260104.sql

# Restore from compressed file
gunzip -c backup-20260104.sql.gz | docker exec -i iau-portal-postgres psql -U iau_admin iau_portal
```

**Full Data Backup (Database + Attachments):**
```bash
# Backup PostgreSQL database + user uploads (signatures/attachments)
tar -czf iau-portal-full-backup-$(date +%Y%m%d).tar.gz \
  /home/addoodi/appdata/iau-portal/data \
  <(docker exec iau-portal-postgres pg_dump -U iau_admin iau_portal)
```

### Database Access

**Connect to PostgreSQL CLI:**
```bash
docker exec -it iau-portal-postgres psql -U iau_admin -d iau_portal
```

**View Database Schema:**
```bash
# Inside psql
\dt                    # List all tables
\d users              # Describe users table
\d+ employees         # Detailed employee table info
```

For detailed schema documentation, see [Gemini-database.md](Gemini-database.md).

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change FRONTEND_PORT in .env
FRONTEND_PORT=3001
```

### Email Not Sending
1. Verify SMTP settings in Site Settings
2. Check email service allows SMTP
3. For Gmail, ensure app password is used
4. Check firewall/security group settings

### Docker Volume Permissions
```bash
# Ensure correct ownership
sudo chown -R 1000:1000 /home/addoodi/appdata/iau-portal/
```

### Database Connection Issues
```bash
# Check if PostgreSQL container is running
docker ps | grep iau-portal-postgres

# View PostgreSQL logs
docker logs iau-portal-postgres

# Restart PostgreSQL container
docker-compose restart postgres

# Test database connection from backend
docker exec -it iau-portal-backend python -c "from backend.database import engine; print(engine.connect())"
```

### Reset Admin Password
```bash
# Access backend container
docker exec -it iau-portal-backend bash

# Run password reset script (if implemented)
python scripts/reset_admin.py
```

## 📝 Development

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
npm test
```

### Building for Production
```bash
# Frontend build
npm run build

# Docker build
docker-compose build
```

### Code Style
- **Python**: Follow PEP 8
- **JavaScript/React**: ESLint configuration
- **Commits**: Conventional Commits format

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software developed for the Institute of Innovation and Entrepreneurship.

## 📧 Support

For issues and questions:
- Create an issue on GitHub
- Contact the development team

## 🙏 Acknowledgments

- Institute of Innovation and Entrepreneurship
- Built with [Claude Code](https://claude.com/claude-code)

---

**Version**: 1.0.0
**Last Updated**: December 2024
**Maintainer**: IAU Development Team
