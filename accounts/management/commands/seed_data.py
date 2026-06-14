import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Student, Department
from teachers.models import Teacher
from courses.models import Course, Enrollment
from attendance.models import Attendance
from results.models import Result

class Command(BaseCommand):
    help = 'Seeds the database with sample AP university data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing old data...')
        Result.objects.all().delete()
        Attendance.objects.all().delete()
        Enrollment.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        # Delete non-superusers
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating Departments...')
        dept_cs, _ = Department.objects.get_or_create(code='CS', defaults={'name': 'Computer Science'})
        dept_ee, _ = Department.objects.get_or_create(code='EE', defaults={'name': 'Electrical Engineering'})
        dept_ece, _ = Department.objects.get_or_create(code='ECE', defaults={'name': 'Electronics and Communication'})
        dept_mech, _ = Department.objects.get_or_create(code='MECH', defaults={'name': 'Mechanical Engineering'})
        
        depts = [dept_cs, dept_ee, dept_ece, dept_mech]

        self.stdout.write('Creating Admin Users...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@nexus.edu', 'admin')
        else:
            u = User.objects.get(username='admin')
            u.set_password('admin')
            u.save()

        if not User.objects.filter(username='vishnu').exists():
            User.objects.create_superuser('vishnu', 'vishnu@nexus.edu', 'vishnu')
        else:
            u = User.objects.get(username='vishnu')
            u.set_password('vishnu')
            u.save()

        teacher_first_names = ['Srinivas', 'Venkat', 'Ram', 'Suresh', 'Ramesh', 'Ravi', 'Prasad', 'Krishna', 'Lakshmi', 'Sunitha', 'Bhavani', 'Padma', 'Harish', 'Kiran']
        teacher_last_names = ['Rao', 'Reddy', 'Naidu', 'Chowdary', 'Murthy', 'Varma', 'Sastry', 'Raju', 'Babu', 'Kumar']

        self.stdout.write('Creating Teachers & HODs...')
        teachers = []
        # Generate 14 teachers
        for i in range(14):
            fname = teacher_first_names[i]
            lname = random.choice(teacher_last_names)
            username = f"{fname.lower()}.{lname.lower()[:1]}"
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            u = User.objects.create_user(username=username, first_name=fname, last_name=lname)
            password = f"{fname.lower()}@123"
            u.set_password(password)
            u.save()

            dept = depts[i % 4]
            is_hod = (i < 4) # First 4 teachers are HODs of the 4 depts
            
            t = Teacher.objects.create(user=u, employee_id=f'T-{100+i}', department=dept, is_hod=is_hod, phone=f'9876543{i:03d}')
            teachers.append(t)

        self.stdout.write('Creating Courses...')
        courses = []
        course_names = ['Data Structures', 'Algorithms', 'Operating Systems', 'Database Systems', 'Circuit Theory', 'Microprocessors', 'VLSI Design', 'Thermodynamics', 'Fluid Mechanics', 'Machine Learning', 'Computer Networks', 'Control Systems']
        for i, cname in enumerate(course_names):
            dept = depts[i % 4]
            t = teachers[i % 14]
            c = Course.objects.create(code=f'{dept.code}{200+i}', name=cname, department=dept, teacher=t)
            courses.append(c)
        
        self.stdout.write('Creating Students...')
        student_first_names = ['Karthik', 'Teja', 'Harsha', 'Sai', 'Akhil', 'Vamsi', 'Pavan', 'Anusha', 'Divya', 'Sowmya', 'Swathi', 'Priyanka', 'Rahul', 'Naveen', 'Tarun', 'Siva', 'Nithin', 'Prasanth', 'Mohan', 'Rajesh', 'Sravani', 'Mounika', 'Anil', 'Sunil', 'Vijay', 'Ajay']
        student_last_names = ['Reddy', 'Naidu', 'Chowdary', 'Rao', 'Varma', 'Goud', 'Shetty', 'Kumar', 'Raju']

        students = []
        # Create 140 unique name combinations
        import itertools
        all_name_combinations = list(itertools.product(student_first_names, student_last_names))
        random.shuffle(all_name_combinations)
        
        # Create 140 students
        for i in range(140):
            fname, lname = all_name_combinations[i]
            username = f"{fname.lower()}{i}"
            
            u = User.objects.create_user(username=username, first_name=fname, last_name=lname)
            password = f"{fname.lower()}@123"
            u.set_password(password)
            u.save()

            dept = random.choice(depts)
            s = Student.objects.create(user=u, roll_number=f'S-2026-{i+1:03d}', department=dept, year=random.randint(1,4), phone=f'9988776{i:03d}')
            students.append(s)

            # Enroll in 3 random courses from their department
            dept_courses = [c for c in courses if c.department == dept]
            if len(dept_courses) >= 3:
                enrolled_courses = random.sample(dept_courses, 3)
            else:
                enrolled_courses = dept_courses

            for course in enrolled_courses:
                Enrollment.objects.create(student=s, course=course)

        self.stdout.write('Generating Attendance & Results...')
        for student in students:
            for enroll in student.enrollments.all():
                course = enroll.course
                
                # Results
                Result.objects.create(
                    student=student, course=course,
                    marks_obtained=random.uniform(40.0, 98.0),
                    total_marks=100.0,
                    remarks='Excellent' if random.random() > 0.8 else ('Good' if random.random() > 0.4 else 'Needs improvement')
                )

                # Attendance (last 10 days)
                for days_ago in range(10):
                    att_date = date.today() - timedelta(days=days_ago)
                    # Exclude weekends randomly
                    if att_date.weekday() < 5:
                        Attendance.objects.create(
                            student=student, course=course, date=att_date,
                            # Each student gets a random personal attendance rate 72%-92%
                            status='P' if random.random() < random.uniform(0.72, 0.92) else 'A'
                        )

        self.stdout.write(self.style.SUCCESS('Database successfully seeded with AP/Indian University data! (14 Teachers, 140 Students)'))
