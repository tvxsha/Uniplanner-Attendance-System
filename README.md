UniPlanner is a web-based Student Attendance Management System built using Flask (Python) and SQLite, designed to simplify attendance tracking for educational institutions. The system provides separate portals for Admin and Students, ensuring clear role-based access and functionality. 
## Features
### Admin Portal
- Secure admin login
- Add and manage students (with photo upload)
- Add and delete subjects
- Specify expected total classes per subject
- Assign subjects to students
- Mark attendance as **Present** or **Absent**
- Automatically track total classes conducted
- View student-wise attendance reports
- Calculate subject-wise attendance percentages
### Student Portal
- Student login using registration number
- View enrolled subjects
- View attendance details for each subject
- Real-time attendance percentage calculation

## Tech Stack

- **Backend**: Python, Flask  
- **Database**: SQLite  
- **ORM**:SQLAlchemy  
- **Frontend:** HTML, CSS, Jinja2
- 
## Project Structure
Uniplanner/
│

├── app.py

├── uniplanner.db

├── requirements.txt

│
├── templates/

│ ├── admin_login.html

│ ├── admin_dashboard.html

│ ├── add_student.html

│ ├── add_subject.html

│ ├── assign_subjects.html

│ ├── mark_attendance.html

│ ├── admin_students.html

│ ├── view_student_attendance.html

│ ├── student_login.html

│ ├── student_dashboard.html

│ ├── base.html

│ └── home.html

│
├── static/

│ ├── styles.css

│ └── uploads/

│
└── venv/

## Setup Instructions

### Clone the Repository
bash
git clone <your-github-repo-link>
cd Uniplanner
### Create and Activate Virtual Environment
bash
Copy code
python -m venv venv
venv\Scripts\activate
### Install Dependencies
bash
Copy code
pip install flask flask-sqlalchemy
### Run the Application
bash
Copy code
python app.py
Application Routes
Home Page: /

Admin Login: /admin/login

Admin Dashboard: /admin/dashboard

Student Login: /student/login

Student Dashboard: /student/dashboard

### Database 
Uses SQLite (uniplanner.db)
Tables:
Student
Subject
Enrollment
Attendance

Database tables are created automatically when the app runs.
