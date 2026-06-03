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

        # ── Courses ──────────────────────────────────────────
        courses_data = [
            ('Python Programming',      'CSE101', 4, depts[0]),
            ('Data Structures',         'CSE102', 4, depts[0]),
            ('Database Management',     'CSE103', 3, depts[0]),
            ('Django Web Development',  'CSE104', 3, depts[0]),
            ('Circuit Theory',          'ECE101', 4, depts[1]),
            ('Digital Electronics',     'ECE102', 3, depts[1]),
            ('Engineering Mechanics',   'MECH101',4, depts[2]),
            ('Thermodynamics',          'MECH102',3, depts[2]),
        ]
        courses = []
        for name, code, credits, dept in courses_data:
            c, _ = Course.objects.get_or_create(
                code=code,
                defaults={'name': name, 'credits': credits, 'department': dept}
            )
            courses.append(c)
        self.stdout.write(f'  [OK] {len(courses)} courses ready')

        # ── Students ─────────────────────────────────────────
        students_data = [
            ('student1', 'Arjun',   'Sharma',  'CSE2022001', depts[0], 3),
            ('student2', 'Priya',   'Patel',   'CSE2022002', depts[0], 3),
            ('student3', 'Rohit',   'Kumar',   'ECE2022001', depts[1], 2),
            ('student4', 'Sneha',   'Reddy',   'CSE2022003', depts[0], 4),
            ('student5', 'Vikram',  'Singh',   'MECH2022001',depts[2], 1),
            ('student6', 'Ananya',  'Iyer',    'CSE2022004', depts[0], 2),
        ]
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
        self.stdout.write('Student login credentials:')
        for uname, *_ in students_data:
            self.stdout.write(f'   Username: {uname}  |  Password: student123')
        self.stdout.write('')
