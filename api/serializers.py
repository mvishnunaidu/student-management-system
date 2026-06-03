from rest_framework import serializers
from students.models import Student, Department
from courses.models import Course, Enrollment
from attendance.models import Attendance
from results.models import Result


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Department
        fields = ['id', 'name', 'code']


class StudentSerializer(serializers.ModelSerializer):
    full_name  = serializers.SerializerMethodField()
    department = DepartmentSerializer(read_only=True)
    email      = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model  = Student
        fields = ['id', 'roll_number', 'full_name', 'email', 'department', 'year', 'phone', 'created_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class CourseSerializer(serializers.ModelSerializer):
    department     = DepartmentSerializer(read_only=True)
    enrolled_count = serializers.SerializerMethodField()

    class Meta:
        model  = Course
        fields = ['id', 'code', 'name', 'credits', 'department', 'enrolled_count']

    def get_enrolled_count(self, obj):
        return obj.enrollments.count()


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_roll = serializers.CharField(source='student.roll_number', read_only=True)
    course_name  = serializers.CharField(source='course.name', read_only=True)
    course_code  = serializers.CharField(source='course.code', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model  = Attendance
        fields = ['id', 'student_name', 'student_roll', 'course_name', 'course_code',
                  'date', 'status', 'status_label']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.username


class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_roll = serializers.CharField(source='student.roll_number', read_only=True)
    course_name  = serializers.CharField(source='course.name', read_only=True)
    percentage   = serializers.FloatField(read_only=True)

    class Meta:
        model  = Result
        fields = ['id', 'student_name', 'student_roll', 'course_name',
                  'marks_obtained', 'total_marks', 'percentage', 'grade']

    def get_student_name(self, obj):
        return obj.student.user.get_full_name() or obj.student.user.username
