# StaffSync — Modern Human Resource Management System

StaffSync is an enterprise-grade, fully functional **MERN-Stack** (MongoDB, Express.js, React.js, Node.js) Human Resource Management System designed to streamline organizational workflows, automate attendance and leave tracking, facilitate internal communications, and provide transparent role-based access for HR Personnel, Department Managers, and Employees.

---

## 🌟 Key Features

### 1. Role-Based Access Control (RBAC)
- **HR Administrator**: Full administrative governance. Manage employee profiles, create announcements, correct attendance records with mandatory audit reasons, configure training programs, review organizational analytics, and export CSV reports.
- **Team Manager**: Supervisory oversight of assigned direct reports. Review team attendance, approve or reject leave requests with decision notes, assign employees to training programs, and monitor team performance.
- **Employee**: Self-service portal. Daily check-in/out with automated duration calculation, view remaining leave balances across categories (Casual, Sick, Earned, Unpaid), submit leave requests, view company news, and track training course progress.

### 2. Core Modules
- **Dynamic Role Dashboards**: Separate metric dashboards tailored to HR Admins, Managers, and Employees with real-time MongoDB aggregations and Recharts data visualizations.
- **Employee Directory & Profiles**: Search by name/ID/email, filter by department, designation, and employment status. View full profile cards including emergency contacts, compensation, and work schedules.
- **Leave Management Workflow**: Validates date ranges, prevents overlapping leave requests, verifies quota balance sufficiency, and allows managers to approve/reject with comments.
- **Attendance Tracking**: Accurate check-in and check-out tracking, automated total duration calculation, late check-in detection, and admin correction with audit logging.
- **Company Announcements & News**: Category filters (General, Policy, Event, Urgent, Holiday), pinned high-priority memos, and instant in-app broadcasting.
- **Training & Skill Development**: Course catalog, cohort capacities, assigned employee tracking, and learner progress updates.
- **In-App Notifications**: Real-time alerts for leave requests, managerial decisions, announcements, and training assignments.
- **Reports & CSV Exports**: One-click export of Employee Master Rosters, Attendance Logs, and Leave Records to standard CSV formats.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, React Router v7, Lucide Icons, Recharts, Axios |
| **Backend** | Node.js, Express.js, JWT, bcryptjs, json2csv, Morgan, Rate Limiting |
| **Database** | MongoDB 9.0 Community Edition / MongoDB Atlas, Mongoose ODM |
| **Security** | Bcrypt salted password hashing, JWT HTTP authorization headers, CORS protection, Rate limiting, Input sanitization |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Node.js** (v18+ or v26+) and **npm** installed.
- **MongoDB** running locally on port `27017` or a MongoDB Atlas connection string.

### 2. Configure Environment Variables
Inside `server/.env`:
```env
PORT=5000
NODE_ENV=development
MONGO_URI=mongodb://127.0.0.1:27017/staffsync
JWT_SECRET=staffsync_super_secret_jwt_key_2026_dev_secure
CLIENT_URL=http://localhost:5173
```

### 3. Seed Database with Realistic HR Data
Populate demo users, employee records, past attendance logs, leave balances, and company announcements:
```bash
cd server
npm run seed
```

### 4. Start the Application

#### Option A: 1-Command Python Master Launcher (Recommended)
You can run the entire application stack (MongoDB + Backend + Frontend + automatic browser launch) with a single Python command:
```bash
python app.py
```
Or check system diagnostics:
```bash
python app.py --check
```

#### Option B: Manual npm scripts

**Start the Backend API (Port 5000)**
```bash
cd server
npm start
```

**Start the Frontend Client (Port 5173)**
```bash
cd client
npm run dev
```

Visit **`http://localhost:5173`** in your browser.

---

## 🔑 Demo Login Accounts

The login page features **1-Click Demo Login buttons** for instant switching between roles during demonstrations:

| Role | Email | Password | Access Capabilities |
|---|---|---|---|
| **HR Administrator** | `admin@staffsync.com` | `admin123` | Full org access, Employee CRUD, System reports, Attendance corrections |
| **Team Manager** | `sarah.manager@staffsync.com` | `manager123` | Engineering team oversight, Leave approvals, Team attendance |
| **Team Manager** | `marcus.manager@staffsync.com` | `manager123` | Marketing team oversight, Leave approvals, Training assignment |
| **Senior Developer** | `alex.dev@staffsync.com` | `employee123` | Self-service attendance check-in/out, Leave applications, Course progress |
| **Frontend Engineer** | `clara.dev@staffsync.com` | `employee123` | Self-service attendance check-in/out, Leave applications, Profile updates |

---

## 📡 REST API Reference

### Authentication (`/api/auth`)
- `POST /api/auth/login` - Authenticate user & return JWT token
- `GET /api/auth/me` - Get authenticated user profile
- `PUT /api/auth/profile` - Update permitted employee contact fields
- `PUT /api/auth/password` - Change password

### Employees (`/api/employees`)
- `GET /api/employees` - List employees with search, department filter & pagination
- `GET /api/employees/:id` - Full employee profile
- `POST /api/employees` - Create employee record & user login (Admin)
- `PUT /api/employees/:id` - Update employee details (Admin)
- `DELETE /api/employees/:id` - Deactivate employee (Admin)
- `GET /api/employees/team/members` - Get manager's direct reports (Manager)

### Leaves (`/api/leaves`)
- `POST /api/leaves/apply` - Submit time-off request
- `GET /api/leaves/my` - View logged-in employee leave history
- `GET /api/leaves/team` - View team leaves awaiting review (Manager)
- `GET /api/leaves/all` - View organization leaves (Admin)
- `PUT /api/leaves/:id/review` - Approve or reject leave with comment (Manager/Admin)
- `PUT /api/leaves/:id/cancel` - Cancel pending leave request
- `GET /api/leaves/balance` - Get employee leave quota balance

### Attendance (`/api/attendance`)
- `POST /api/attendance/check-in` - Record check-in timestamp
- `POST /api/attendance/check-out` - Record check-out & compute duration
- `GET /api/attendance/today` - Today's check-in status
- `GET /api/attendance/my` - Monthly attendance history
- `GET /api/attendance/team` - Team daily attendance roster
- `GET /api/attendance/all` - Organization-wide attendance (Admin)
- `PUT /api/attendance/:id/correct` - Manual attendance correction with reason (Admin)

### Reports & CSV Exports (`/api/reports`)
- `GET /api/reports/analytics` - Aggregated HR analytics metrics
- `GET /api/reports/attendance/csv` - Stream attendance data in CSV
- `GET /api/reports/employees/csv` - Stream employee directory in CSV
- `GET /api/reports/leaves/csv` - Stream leave history in CSV

---

## 🛡️ Security Best Practices
- Passwords hashed using bcrypt with salt rounds of 10.
- Sensitive fields like salary masked for non-authorized roles.
- Strict token-based authentication on all private API endpoints.
- Audit logging for administrative events (Leave reviews, Attendance corrections, Account status changes).
