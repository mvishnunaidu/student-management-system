from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from students.models import Student
from courses.models import Course
from attendance.models import Attendance
from results.models import Result
from .serializers import (
    StudentSerializer, CourseSerializer,
    AttendanceSerializer, ResultSerializer
)


class StudentListAPIView(APIView):
    """
    GET /api/students/
    Returns list of all students.
    Requires: Authorization: Bearer <access_token>
    """
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request):
        students   = Student.objects.select_related('user', 'department').all()
        serializer = StudentSerializer(students, many=True)
        return Response({'count': students.count(), 'students': serializer.data})


class CourseListAPIView(APIView):
    """
    GET /api/courses/
    Returns list of all courses.
    Requires: Authorization: Bearer <access_token>
    """
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request):
        courses    = Course.objects.select_related('department').all()
        serializer = CourseSerializer(courses, many=True)
        return Response({'count': courses.count(), 'courses': serializer.data})


class AttendanceAPIView(APIView):
    """
    GET /api/attendance/?student_id=X&course_id=Y
    Returns attendance records (filterable).
    Requires: Authorization: Bearer <access_token>
    """
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request):
        qs = Attendance.objects.select_related('student__user', 'course').all()
        student_id = request.query_params.get('student_id')
        course_id  = request.query_params.get('course_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if course_id:
            qs = qs.filter(course_id=course_id)
        serializer = AttendanceSerializer(qs[:100], many=True)
        return Response({'count': qs.count(), 'results': serializer.data})


class ResultAPIView(APIView):
    """
    GET /api/results/?student_id=X
    Returns results (filterable).
    Requires: Authorization: Bearer <access_token>
    """
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request):
        qs = Result.objects.select_related('student__user', 'course').all()
        student_id = request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        serializer = ResultSerializer(qs, many=True)
        return Response({'count': qs.count(), 'results': serializer.data})
