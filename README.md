# 🎓 Nexus University Portal

<div align="center">

[![Django](https://img.shields.io/badge/Django-4.2_LTS-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DRF](https://img.shields.io/badge/REST_API-DRF-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![JWT](https://img.shields.io/badge/Auth-JWT-orange?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://django-rest-framework-simplejwt.readthedocs.io/)
[![MySQL](https://img.shields.io/badge/Database-MySQL-00758F?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/UI-Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)

**A full-stack University Portal with Role-Based Access Control, Attendance Tracking, Results Management, and a JWT-secured REST API.**

*Built with Django 4.2 LTS · 140 Students · 14 Teachers · 12 Courses · 82.4% Avg Attendance*

</div>

---

## 📌 About The Project

**Nexus University Portal** is a production-style academic management system where **Admins**, **Teachers/HODs**, and **Students** each log in to a personalized dashboard showing only their relevant data.

This project was built as a **fresher Django portfolio project** to demonstrate:
- Full-stack web development with Django
- Role-Based Access Control (RBAC)
- REST API design with JWT authentication
- Database design with relational models
- Modern responsive UI with animations

---

## ✨ Features

### 👑 Admin
- View all Students, Teachers, HODs, Departments, Courses
- Add / Edit / Delete any record
- View full attendance reports and all results
- Access Django Admin panel at `/admin/`

### 👨‍🏫 Teacher / HOD
- Personal dashboard showing their assigned courses
- Mark attendance for their course students
- View results for students in their courses
- HODs have a special badge in the system

### 🎓 Student
- View their own profile, enrolled courses
- Check personal attendance percentage
- View their own mid/final exam results and grades
- Cannot see other students' data (data isolation)

### 🔌 REST API
- JWT-secured endpoints for all resources
- Filterable attendance and results by student ID
- Token refresh support

### 🎨 Modern UI
- Glassmorphism cards with animated gradients
- Sky-blue attendance card (≥72%) / Amber warning card (<72%)
- Dark / Light theme toggle
- Floating icons, pulsing animations, Chart.js charts
- Password show/hide toggle on login

---

## 🗄️ Database Schema

```
User ──1:1── Student ──── Department
                │               │
           Enrollment ───── Course ──── Teacher (HOD flag)
                │
          Attendance (P/A/L per course per day)
          Result     (marks → auto grade A+/A/B+/B/C/D/F)
```

**Relational integrity:**  
- `unique_together` on (Student, Course, Date) for attendance  
- `unique_together` on (Student, Course) for results  
- Grades auto-calculated in `Result.save()` override  

---

## 🗂️ Project Structure

```
student_management_system/
├── sms/              → Settings, root URLs, WSGI
├── accounts/         → Login, Register, Dashboard, seed_data command
├── students/         → Student CRUD, Department model
├── teachers/         → Teacher CRUD, HOD flag
├── courses/          → Course CRUD, Enrollment model
├── attendance/       → Attendance marking, reports, student view
├── results/          → Results CRUD, auto-grading
├── api/              → DRF ViewSets, Serializers, JWT
├── templates/        → HTML (base.html + per-app templates)
├── static/           → CSS (Glassmorphism), JS (theme, sidebar)
├── .env.example      → Environment variable template
├── requirements.txt  → All Python dependencies
└── manage.py
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- MySQL Server running locally
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/student_management_system.git
cd student_management_system
```

### 2. Create & Activate Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
copy .env.example .env      # Windows
# cp .env.example .env      # Linux/Mac
```
Edit `.env` and set your MySQL credentials:
```env
DB_NAME=student_management
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY=your-long-random-secret-key
DEBUG=True
```

### 5. Create MySQL Database
```sql
CREATE DATABASE student_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Seed the Database (One Command!)
```bash
python manage.py seed_data
```
This creates:
- **2 Admin accounts** (admin/admin, vishnu/vishnu)
- **14 Teachers** with AP Telugu names (4 HODs)
- **140 Students** with AP Telugu names
- **12 Courses** across 4 departments
- **2,520 Attendance records** → Avg **82.4%**
- **420 Result records** with auto-graded marks

### 8. Run the Development Server
```bash
python manage.py runserver
```
Open: **http://127.0.0.1:8000**

---

## 🔑 Login Credentials

| Role | Username | Password |
|:---:|:---:|:---:|
| 👑 Admin | `admin` | `admin` |
| 👑 Admin | `vishnu` | `vishnu` |
| 👨‍🏫 Teacher (HOD) | `srinivas.r` | `srinivas@123` |
| 👨‍🏫 Teacher | `bhavani.b` | `bhavani@123` |
| 🎓 Student | `naveen0` | `naveen@123` |
| 🎓 Student | `anusha1` | `anusha@123` |

> **Pattern:** All passwords = `firstname@123`  
> Examples: `karthik@123`, `lakshmi@123`, `divya@123`

---

## 🔌 REST API Reference

Base URL: `http://127.0.0.1:8000/api/`

### Step 1 — Get Access Token
```http
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```
Response:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Step 2 — Use Token in Requests
```http
GET /api/students/
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Available Endpoints

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/token/` | Get JWT access + refresh token |
| `POST` | `/api/token/refresh/` | Refresh expired access token |
| `GET` | `/api/students/` | List all students |
| `GET` | `/api/courses/` | List all courses |
| `GET` | `/api/attendance/?student_id=1` | Student attendance records |
| `GET` | `/api/results/?student_id=1` | Student result records |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.10+, Django 4.2 LTS | Core web framework |
| **Database** | MySQL + PyMySQL | Relational data storage |
| **REST API** | Django REST Framework | API endpoints |
| **Auth** | SimpleJWT | JWT token authentication |
| **Frontend** | Bootstrap 5 + Vanilla CSS | Responsive UI |
| **Charts** | Chart.js | Department + enrollment charts |
| **Fonts** | Google Fonts (Outfit, Inter) | Typography |
| **Icons** | Bootstrap Icons | UI iconography |

---

## 💡 Technical Highlights

| # | Pattern | Implementation |
|---|---|---|
| 1 | **RBAC** | `is_staff` flag + `student_profile`/`teacher_profile` relations |
| 2 | **Auto-Grading** | `Result.save()` override computes grade from `marks_obtained` |
| 3 | **ORM Optimization** | `select_related()` and `prefetch_related()` prevent N+1 queries |
| 4 | **Data Isolation** | Students query filtered by `student=request.user.student_profile` |
| 5 | **JWT Security** | 1-hour access tokens, 1-day refresh tokens |
| 6 | **Seeding** | `manage.py seed_data` one command for full realistic data |
| 7 | **Unique Constraints** | `unique_together` prevents duplicate attendance/results |

---

## 📦 Sample Data Stats

| Item | Count |
|---|---|
| Students | 140 (AP Telugu names) |
| Teachers | 14 (4 HODs) |
| Departments | 4 (CS, EE, ECE, MECH) |
| Courses | 12 |
| Enrollments | 420 |
| Attendance records | 2,520 |
| Result records | 420 |
| **Avg Attendance** | **82.4%** |

---

## 🚀 Deployment

| Platform | Status | Notes |
|---|---|---|
| **PythonAnywhere** | ✅ Recommended (Free) | Supports MySQL, easy Django setup |
| **Railway.app** | ✅ Works | Supports MySQL |
| **Render.com** | ⚠️ Needs change | Switch to PostgreSQL |
| **VPS / DigitalOcean** | ✅ Works | Full control |

---

<div align="center">

**Made with ❤️ using Django · A fresher Django portfolio project**

</div>
