from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime

print("DEBUG FLASH IMPORT:", flash)

app = Flask(__name__)
app.secret_key = "secret123"

# config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///uniplanner.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# models

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(200))


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_classes = db.Column(db.Integer, default=0)
    expected_total_classes = db.Column(db.Integer, nullable=False)


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))

    student = db.relationship("Student")
    subject = db.relationship("Subject")


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"))
    present = db.Column(db.Boolean)
    class_date = db.Column(db.Date, default=datetime.utcnow().date)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)

# init db

with app.app_context():
    db.create_all()

# admin login

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

# admin dashboard

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    return render_template(
        "admin_dashboard.html",
        students_count=Student.query.count(),
        subjects_count=Subject.query.count()
    )

# add student

@app.route("/admin/add-student", methods=["GET", "POST"])
def add_student():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        file = request.files["photo"]
        filename = None

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        student = Student(
            reg_no=request.form["reg_no"],
            name=request.form["name"],
            photo=filename
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))

    return render_template("add_student.html")

# add subject

@app.route("/admin/add-subject", methods=["GET", "POST"])
def add_subject():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        subject = Subject(
            name=request.form["name"],
            expected_total_classes=int(request.form["expected_total_classes"]),
            total_classes=0
        )
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for("add_subject"))

    return render_template("add_subject.html", subjects=Subject.query.all())

# delete subject

@app.route("/admin/delete-subject/<int:id>")
def delete_subject(id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    Subject.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for("add_subject"))

# assign subject

@app.route("/admin/assign-subjects", methods=["GET", "POST"])
def assign_subjects():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    students = Student.query.all()
    subjects = Subject.query.all()

    if request.method == "POST":
        enrollment = Enrollment(
            student_id=request.form["student_id"],
            subject_id=request.form["subject_id"]
        )
        db.session.add(enrollment)
        db.session.commit()

    return render_template(
        "assign_subjects.html",
        students=students,
        subjects=subjects
    )
# mark attendence
@app.route("/admin/mark-attendance", methods=["GET", "POST"])
def mark_attendance():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    enrollments = Enrollment.query.all()

    if request.method == "POST":
        enrollment_id = int(request.form["enrollment_id"])
        status = request.form["status"]
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            return render_template("mark_attendance.html", enrollments=enrollments)
        is_present = True if status == "present" else False
        

        # read class date and time range from form
        class_date_str = request.form.get("class_date")
        start_time_str = request.form.get("start_time")
        end_time_str = request.form.get("end_time")

        # parse date (fallback to today if missing)
        if class_date_str:
            class_date = datetime.strptime(class_date_str, "%Y-%m-%d").date()
        else:
            class_date = datetime.utcnow().date()

        # parse start/end times (optional)
        start_time = None
        if start_time_str:
            start_time = datetime.strptime(start_time_str, "%H:%M").time()

        end_time = None
        if end_time_str:
            end_time = datetime.strptime(end_time_str, "%H:%M").time()

        # create Attendance with date and time range
        attendance = Attendance(
            student_id=enrollment.student_id,
            subject_id=enrollment.subject_id,
            present=is_present,
            class_date=class_date,
            start_time=start_time,
            end_time=end_time
        )

        db.session.add(attendance)

        # increase total classes ONLY ONCE per class
        subject = Subject.query.get(enrollment.subject_id)
        subject.total_classes += 1

        db.session.commit()

    return render_template(
        "mark_attendance.html",
        enrollments=enrollments
    )


# view students

@app.route("/admin/students")
def admin_students():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    return render_template(
        "admin_students.html",
        students=Student.query.all()
    )

# view student attendence

@app.route("/admin/student/<int:student_id>/attendance")
def view_student_attendance(student_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    student = Student.query.get_or_404(student_id)

    attendance_data = []

    # get unique subjects for student
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    subjects = {e.subject for e in enrollments}

    for subject in subjects:
        attended = Attendance.query.filter_by(
            student_id=student_id,
            subject_id=subject.id,
            present=True
        ).count()

        total = Attendance.query.filter_by(
            student_id=student_id,
            subject_id=subject.id
        ).count()

        percent = round((attended / total) * 100, 2) if total > 0 else 0

        attendance_data.append({
            "subject": subject.name,
            "attended": attended,
            "total": total,
            "percent": percent
        })

    return render_template(
        "view_student_attendance.html",
        student=student,
        attendance=attendance_data
    )


#student login

@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        reg_no = request.form.get("reg_no")

        student = Student.query.filter_by(reg_no=reg_no).first()

        if student:
            session["student_id"] = student.id
            return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid registration number")

    return render_template("student_login.html")

# student dashboard

@app.route("/student/dashboard")
def student_dashboard():
    if not session.get("student_id"):
        return redirect(url_for("student_login"))

    student = Student.query.get(session["student_id"])
    if not student:
        # session pointing to a student that no longer exists
        session.pop("student_id", None)
        return redirect(url_for("student_login"))

    attendance_data = []

    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    subjects = {e.subject for e in enrollments}

    for subject in subjects:
        attended = Attendance.query.filter_by(
            student_id=student.id,
            subject_id=subject.id,
            present=True
        ).count()

        total = Attendance.query.filter_by(
            student_id=student.id,
            subject_id=subject.id
        ).count()

        percent = round((attended / total) * 100, 2) if total > 0 else 0

        attendance_data.append({
            "subject": subject.name,
            "attended": attended,
            "total": total,
            "percent": percent
        })

    # --- NEW: build recent_classes with subject name ---
    recent_classes = (
        db.session.query(Attendance, Subject)
        .join(Subject, Attendance.subject_id == Subject.id)
        .filter(Attendance.student_id == student.id)
        .order_by(Attendance.class_date.desc(), Attendance.start_time.desc())
        .limit(20)
        .all()
    )

    recent_class_rows = []
    for att, subj in recent_classes:
        recent_class_rows.append({
            "date": att.class_date,
            "start_time": att.start_time,
            "end_time": att.end_time,
            "subject_name": subj.name,
            "present": att.present,
        })

    return render_template(
        "student_dashboard.html",
        student=student,
        attendance=attendance_data,
        recent_classes=recent_class_rows,
        timetable=None
    )



#student logout 
@app.route("/student/logout")
def student_logout():
    session.pop("student_id", None)
    return redirect(url_for("student_login"))
#home
@app.route("/")
def home():
    return render_template("home.html")



# run
if __name__ == "__main__":
    app.run(debug=True)
