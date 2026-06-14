from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from students.models import Department, Student
from courses.models import Course, Enrollment
from attendance.models import Attendance
from results.models import Result
from rest_framework import status
import datetime

class StudentManagementSystemTests(TestCase):
    def setUp(self):
        # Create a test department
        self.dept = Department.objects.create(name="Computer Science", code="CSE", description="CS Dept")
        
        # Create a staff user (admin) and a normal user (student)
        self.admin_user = User.objects.create_superuser(username='testadmin', password='adminpassword', email='admin@test.com')
        self.student_user = User.objects.create_user(username='teststudent', password='studentpassword', email='student@test.com')
        
        # Create a Student profile
        self.student = Student.objects.create(
            user=self.student_user,
            roll_number="CSE001",
            department=self.dept,
            year=3,
            phone="1234567890"
        )
        
        # Create a course
        self.course = Course.objects.create(
            name="Introduction to Python",
            code="CSE101",
            credits=4,
            department=self.dept
        )
        
        # Enroll student in course
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)

    def test_dashboard_view_requires_login(self):
        client = Client()
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_dashboard_view_authenticated(self):
        client = Client()
        client.login(username='testadmin', password='adminpassword')
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")
        self.assertContains(response, "Total Students")

    def test_student_list_view(self):
        client = Client()
        client.login(username='testadmin', password='adminpassword')
        response = client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CSE001")

    def test_student_detail_view(self):
        client = Client()
        client.login(username='teststudent', password='studentpassword')
        response = client.get(reverse('student_detail', kwargs={'pk': self.student.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CSE001")
        self.assertContains(response, "Introduction to Python")

    def test_student_add_by_non_admin_fails(self):
        client = Client()
        client.login(username='teststudent', password='studentpassword')
        response = client.post(reverse('student_add'), {
            'username': 'newstudent',
            'first_name': 'New',
            'last_name': 'Student',
            'roll_number': 'CSE002',
            'department': self.dept.id,
            'year': 1,
        })
        self.assertEqual(response.status_code, 302) # Redirects with error
        self.assertFalse(User.objects.filter(username='newstudent').exists())

    def test_student_add_by_admin_succeeds(self):
        client = Client()
        client.login(username='testadmin', password='adminpassword')
        response = client.post(reverse('student_add'), {
            'username': 'newstudent',
            'first_name': 'New',
            'last_name': 'Student',
            'roll_number': 'CSE002',
            'department': self.dept.id,
            'year': 1,
            'phone': '9876543210'
        })
        self.assertEqual(response.status_code, 302) # Redirects to list
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertTrue(Student.objects.filter(roll_number='CSE002').exists())

    def test_api_jwt_token_and_endpoints(self):
        # 1. Obtain Token
        client = Client()
        response = client.post(reverse('token_obtain_pair'), {
            'username': 'teststudent',
            'password': 'studentpassword'
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.json().get('access')
        self.assertIsNotNone(access_token)

        # 2. Get students via REST API with Token
        auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
        response = client.get(reverse('api_students'), **auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('students', response.json())
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['students'][0]['roll_number'], 'CSE001')

        # 3. Get courses via REST API with Token
        response = client.get(reverse('api_courses'), **auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('courses', response.json())
        self.assertEqual(response.json()['courses'][0]['code'], 'CSE101')
