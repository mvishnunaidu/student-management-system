"""
Management command to populate the database with sample data.
Run: python manage.py populate_data
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Department, Student
from courses.models import Course, Enrollment
from attendance.models import Attendance
from results.models import Result
from teachers.models import Teacher


class Command(BaseCommand):
    help = 'Populate database with sample/dummy data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Creating sample data...'))

        # ── Departments ──────────────────────────────────────
        depts_data = [
            ('Computer Science Engineering', 'CSE'),
            ('Electronics & Communication', 'ECE'),
            ('Mechanical Engineering',       'MECH'),
        ]
        depts = []
        for name, code in depts_data:
            d, _ = Department.objects.get_or_create(code=code, defaults={'name': name})
            depts.append(d)
        self.stdout.write(f'  [OK] {len(depts)} departments ready')

        # ── Teachers ─────────────────────────────────────────
        teachers_data = [
            ('teacher1', 'Alan', 'Turing', 'EMP001', depts[0]),
            ('teacher2', 'Grace', 'Hopper', 'EMP002', depts[0]),
            ('teacher3', 'Nikola', 'Tesla', 'EMP003', depts[1]),
            ('teacher4', 'Marie', 'Curie', 'EMP004', depts[1]),
            ('teacher5', 'Isaac', 'Newton', 'EMP005', depts[2]),
        ]
        teachers = []
        for uname, fname, lname, emp_id, dept in teachers_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={'first_name': fname, 'last_name': lname, 'email': f'{uname}@college.edu'}
            )
            if created:
                user.set_password('teacher123')
                user.save()
            t, _ = Teacher.objects.get_or_create(
                employee_id=emp_id,
                defaults={'user': user, 'department': dept, 'phone': '9876543210'}
            )
            teachers.append(t)
        self.stdout.write(f'  [OK] {len(teachers)} teachers ready')

        # ── Courses ──────────────────────────────────────────
        courses_data = [
            ('Python Programming',      'CSE101', 4, depts[0], teachers[0]),
            ('Data Structures',         'CSE102', 4, depts[0], teachers[1]),
            ('Database Management',     'CSE103', 3, depts[0], teachers[0]),
            ('Django Web Development',  'CSE104', 3, depts[0], teachers[1]),
            ('Circuit Theory',          'ECE101', 4, depts[1], teachers[2]),
            ('Digital Electronics',     'ECE102', 3, depts[1], teachers[3]),
            ('Engineering Mechanics',   'MECH101',4, depts[2], teachers[4]),
            ('Thermodynamics',          'MECH102',3, depts[2], teachers[4]),
        ]
        courses = []
        for name, code, credits, dept, teacher in courses_data:
            c, _ = Course.objects.get_or_create(
                code=code,
                defaults={'name': name, 'credits': credits, 'department': dept, 'teacher': teacher}
            )
            courses.append(c)
        self.stdout.write(f'  [OK] {len(courses)} courses ready')

        # ── Students ─────────────────────────────────────────
        first_names = ['Arjun', 'Priya', 'Rohit', 'Sneha', 'Vikram', 'Ananya', 'Rahul', 'Neha', 'Karan', 'Pooja', 'Amit', 'Divya', 'Sanjay', 'Riya', 'Ravi', 'Kavita', 'Aditya', 'Meera', 'Kunal', 'Swati']
        last_names = ['Sharma', 'Patel', 'Kumar', 'Reddy', 'Singh', 'Iyer', 'Gupta', 'Verma', 'Desai', 'Joshi', 'Nair', 'Menon', 'Rao', 'Das', 'Bose', 'Chopra', 'Malhotra', 'Bhat', 'Jain', 'Kaur']
        
        students_data = []
        for i in range(1, 51):
            uname = f'student{i}'
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            dept = random.choice(depts)
            year = random.randint(1, 4)
            roll = f'{dept.code}2022{i:03d}'
            students_data.append((uname, fname, lname, roll, dept, year))
        students = []
        for uname, fname, lname, roll, dept, year in students_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={'first_name': fname, 'last_name': lname,
                          'email': f'{uname}@college.edu'}
            )
            if created:
                user.set_password('student123')
                user.save()
            st, _ = Student.objects.get_or_create(
                roll_number=roll,
                defaults={'user': user, 'department': dept, 'year': year,
                          'phone': f'9{random.randint(100000000,999999999)}'}
            )
            students.append(st)
        self.stdout.write(f'  [OK] {len(students)} students ready')

        # ── Enrollments ──────────────────────────────────────
        cse_courses  = courses[:4]
        ece_courses  = courses[4:6]
        mech_courses = courses[6:]

        for st in students:
            if st.department and st.department.code == 'CSE':
                for c in cse_courses:
                    Enrollment.objects.get_or_create(student=st, course=c)
            elif st.department and st.department.code == 'ECE':
                for c in ece_courses:
                    Enrollment.objects.get_or_create(student=st, course=c)
            elif st.department and st.department.code == 'MECH':
                for c in mech_courses:
                    Enrollment.objects.get_or_create(student=st, course=c)
        self.stdout.write('  [OK] Enrollments created')

        # ── Attendance (last 15 days) ─────────────────────────
        pool = ['P','P','P','P','P','P','A','P','L','P','P','P','A','P','P']
        for en in Enrollment.objects.all():
            for i in range(1, 16):
                att_date = date.today() - timedelta(days=i)
                Attendance.objects.get_or_create(
                    student=en.student, course=en.course, date=att_date,
                    defaults={'status': random.choice(pool)}
                )
        self.stdout.write('  [OK] Attendance records created')

        # ── Results ──────────────────────────────────────────
        for en in Enrollment.objects.all():
            marks = round(random.uniform(52, 98), 1)
            Result.objects.get_or_create(
                student=en.student, course=en.course,
                defaults={'marks_obtained': marks, 'total_marks': 100,
                          'exam_date': date.today() - timedelta(days=45)}
            )
        self.stdout.write('  [OK] Results created')

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Sample data loaded successfully!\n'))
        self.stdout.write(f'Generated 5 teachers. Logins: teacher1 to teacher5 | Password: teacher123')
        self.stdout.write(f'Generated {len(students_data)} students. Logins: student1 to student50 | Password: student123')
        self.stdout.write('')
