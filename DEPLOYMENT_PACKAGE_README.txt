================================================================================
IAU PORTAL - DEPLOYMENT PACKAGE
================================================================================

Package Name: iau-portal-deployment.zip
Created: 2026-01-04
Version: 1.0.0
Size: 1.1 MB (compressed), 1.7 MB (uncompressed)
Files: 108 files

================================================================================
PACKAGE CONTENTS
================================================================================

This deployment package contains ALL necessary files to run the IAU Portal
application. No additional files are required except for runtime data.

📁 DIRECTORY STRUCTURE:
-----------------------
.claude/                    - Development plans and local settings
backend/                    - FastAPI backend application (Python)
public/                     - React public assets
src/                        - React frontend source code (JavaScript)

📄 ESSENTIAL FILES:
-------------------
docker-compose.yml          - Docker orchestration configuration
Dockerfile.backend          - Backend container definition
Dockerfile.frontend         - Frontend container definition
nginx.conf                  - Nginx reverse proxy configuration
package.json                - Frontend dependencies (npm)
requirements.txt            - Backend dependencies (Python)
vite.config.js              - Vite build configuration
tailwind.config.js          - Tailwind CSS configuration

📚 DOCUMENTATION FILES:
-----------------------
CLAUDE.md                   - Complete development context for AI assistants
Gemini.md                   - Technical development history (693 lines)
Gemini-database.md          - PostgreSQL schema reference (432 lines)
form-guide.md               - Document template guide
README.md                   - User deployment guide

🔧 CONFIGURATION FILES:
-----------------------
.env.example                - Environment variables template
.env.docker.example         - Docker-specific environment template
.env.portainer.example      - Portainer deployment template
.gitignore                  - Git ignore patterns
.dockerignore               - Docker ignore patterns

================================================================================
BACKEND FILES (backend/)
================================================================================

Core Application:
-----------------
main.py                     - FastAPI application & API endpoints
models.py                   - Pydantic data models
database.py                 - SQLAlchemy models & PostgreSQL setup
db_repositories.py          - PostgreSQL data access layer
services.py                 - Business logic layer
auth.py                     - JWT authentication
dependencies.py             - Dependency injection
calculation.py              - Vacation balance calculations
document_generator.py       - DOCX document generation
email_service.py            - Email notification service
email_templates.py          - HTML email templates
notification_scheduler.py   - Automated task scheduler

Data & Templates:
-----------------
data/.gitkeep               - Empty data directory (created by Docker volumes)
templates/                  - DOCX templates directory

================================================================================
FRONTEND FILES (src/)
================================================================================

Pages:
------
pages/Dashboard.jsx         - Main dashboard
pages/MyRequests.jsx        - Employee leave requests
pages/Approvals.jsx         - Manager approval workflow
pages/UserManagement.jsx    - Admin user management
pages/UnitManagement.jsx    - Admin unit management
pages/SiteSettings.jsx      - Admin settings
pages/EmployeeDetail.jsx    - Employee detail view

Components:
-----------
components/Sidebar.jsx      - Navigation sidebar
components/TopBar.jsx       - Top navigation bar
components/HeaderBanner.jsx - Page header with image
components/RequestModal.jsx - Leave request form modal
components/AddUserModal.jsx - Add user form modal
components/AddUnitModal.jsx - Add unit form modal
components/SignatureModal.jsx - Signature upload modal

Context & Utils:
----------------
context/PortalContext.jsx   - Global state management
utils/translations.js       - Bilingual strings (AR/EN)
api.js                      - Backend API client
App.jsx                     - Main React app
index.jsx                   - React entry point
index.css                   - Tailwind CSS imports

Assets:
-------
assets/images/              - Images (banners, logos, backgrounds)

================================================================================
QUICK START DEPLOYMENT
================================================================================

OPTION 1: Docker Deployment (Recommended)
------------------------------------------
1. Extract the zip file:
   unzip iau-portal-deployment.zip -d iau-portal

2. Navigate to the directory:
   cd iau-portal

3. Create data directories (Linux/Mac):
   mkdir -p /home/addoodi/appdata/iau-portal/data
   mkdir -p /home/addoodi/appdata/iau-portal/templates

   Or (Windows):
   mkdir C:\appdata\iau-portal\data
   mkdir C:\appdata\iau-portal\templates

4. (Optional) Configure environment:
   cp .env.example .env
   # Edit .env to customize settings

5. Start the application:
   docker-compose up -d

6. Access the portal:
   http://localhost:3000

7. First-time setup:
   - Create admin account when prompted
   - Configure email settings in Site Settings

OPTION 2: Local Development
----------------------------
1. Extract the zip file

2. Install backend dependencies:
   pip install -r requirements.txt

3. Install frontend dependencies:
   npm install

4. Start PostgreSQL:
   docker-compose up -d postgres

5. Start backend (terminal 1):
   uvicorn backend.main:app --reload --port 8000

6. Start frontend (terminal 2):
   npm start

7. Access:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

================================================================================
SYSTEM REQUIREMENTS
================================================================================

For Docker Deployment:
----------------------
- Docker 20.10+
- Docker Compose 2.0+
- 4 GB RAM minimum, 8 GB recommended
- 20 GB free disk space
- Linux, Windows Server 2019+, or macOS

For Local Development:
----------------------
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 16 (or via Docker)
- 4 GB RAM minimum
- 10 GB free disk space

================================================================================
WHAT'S NOT INCLUDED (BY DESIGN)
================================================================================

The following are intentionally excluded and will be created at runtime:

❌ node_modules/           - Install with: npm install
❌ __pycache__/            - Created by Python automatically
❌ build/                  - Created by: npm run build
❌ venv/                   - Create with: python -m venv venv
❌ .git/                   - Initialize with: git init

❌ backend/data/*.csv      - Created by application (contains sensitive data)
❌ backend/data/signatures/ - Created by Docker volumes
❌ backend/data/attachments/ - Created by Docker volumes

❌ .env                    - Copy from .env.example and customize

================================================================================
DATABASE SETUP
================================================================================

The application uses PostgreSQL 16 Alpine for data storage.

Docker Deployment:
------------------
PostgreSQL is automatically started via docker-compose.yml.
Database tables are created automatically on first run.

Default Credentials (CHANGE IN PRODUCTION):
- Username: iau_admin
- Password: iau_secure_password_2024
- Database: iau_portal
- Port: 5432 (internal to Docker network)

Database Schema:
----------------
- users              - User accounts & authentication
- employees          - Employee profiles & contracts
- units              - Organizational units
- leave_requests     - Vacation requests
- attendance_logs    - Check-in/check-out records
- email_settings     - SMTP configuration

For detailed schema documentation, see Gemini-database.md.

================================================================================
BACKUP & RESTORE
================================================================================

Backup Database:
----------------
docker exec iau-portal-postgres pg_dump -U iau_admin iau_portal > backup.sql

Backup with Compression:
------------------------
docker exec iau-portal-postgres pg_dump -U iau_admin iau_portal | gzip > backup.sql.gz

Restore Database:
-----------------
docker exec -i iau-portal-postgres psql -U iau_admin iau_portal < backup.sql

Full Backup (Database + Files):
--------------------------------
tar -czf iau-portal-full-backup-$(date +%Y%m%d).tar.gz \
  /home/addoodi/appdata/iau-portal/data \
  <(docker exec iau-portal-postgres pg_dump -U iau_admin iau_portal)

================================================================================
DOCUMENTATION REFERENCE
================================================================================

For detailed information, refer to these files included in the package:

📖 README.md               - User deployment guide
📖 CLAUDE.md               - Complete development context (38,857 bytes)
📖 Gemini.md               - Technical development history (23,462 bytes)
📖 Gemini-database.md      - Database schema reference (15,895 bytes)
📖 form-guide.md           - Document template guide (4,340 bytes)

================================================================================
TECHNOLOGY STACK
================================================================================

Frontend:
---------
- React 19.2.0
- Vite 7.3.0
- Tailwind CSS 3.4.17
- React Router 7.10.1
- Lucide React (icons)
- Recharts (dashboard)

Backend:
--------
- FastAPI (Python)
- SQLAlchemy 2.0+
- Pydantic
- PostgreSQL 16 Alpine
- JWT Authentication
- Uvicorn (ASGI server)

Infrastructure:
---------------
- Docker & Docker Compose
- Nginx (reverse proxy)
- PostgreSQL 16 Alpine

================================================================================
SECURITY NOTES
================================================================================

🔐 BEFORE PRODUCTION DEPLOYMENT:

1. Change default database credentials in docker-compose.yml
2. Generate new JWT SECRET_KEY in .env
3. Configure proper CORS origins (not "*")
4. Enable HTTPS with SSL certificates
5. Review and update .env.example settings
6. Set strong admin password on first login
7. Configure firewall rules (only ports 80, 443)
8. Enable regular automated backups

================================================================================
SUPPORT & CONTACT
================================================================================

📧 For issues and questions:
   - Review documentation files (README.md, CLAUDE.md)
   - Check GitHub repository: https://github.com/addoodi/iau-portal
   - Contact IAU Development Team

🏢 Institute of Innovation and Entrepreneurship
   Imam Abdulrahman Bin Faisal University

================================================================================
LICENSE & CREDITS
================================================================================

Proprietary software developed for the Institute of Innovation and
Entrepreneurship.

Built with Claude Code (https://claude.com/claude-code)
Last Updated: January 4, 2026
Version: 1.0.0

================================================================================
END OF DEPLOYMENT PACKAGE README
================================================================================
