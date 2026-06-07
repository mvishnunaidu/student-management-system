from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from students.models import Student, Department
from courses.models import Course, Enrollment
from attendance.models import Attendance
from results.models import Result
from .forms import LoginForm, RegisterForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Student.objects.create(
                user=user,
                roll_number=form.cleaned_data['roll_number'],
                phone=form.cleaned_data.get('phone', ''),
            )
            messages.success(request, 'Account created! Please login.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    is_teacher = hasattr(request.user, 'teacher_profile')
    is_student = hasattr(request.user, 'student_profile')

    if is_teacher:
        teacher = request.user.teacher_profile
        my_courses = teacher.assigned_courses.all()
        total_courses = my_courses.count()
        total_students = Student.objects.filter(enrollments__course__in=my_courses).distinct().count()
        total_departments = 1
        
        total_att = Attendance.objects.filter(course__in=my_courses).count()
        present_att = Attendance.objects.filter(course__in=my_courses, status='P').count()
        att_pct = round(present_att / total_att * 100, 1) if total_att else 0
        
        recent_students = Student.objects.filter(enrollments__course__in=my_courses).select_related('user', 'department').distinct().order_by('-created_at')[:5]
        recent_results = Result.objects.filter(course__in=my_courses).select_related('student__user', 'course').order_by('-created_at')[:5]
        
        dept_data = [{'name': teacher.department.name if teacher.department else 'N/A', 'count': total_students}]
        course_data = [{'name': c.name, 'code': c.code, 'count': c.enrollments.count()} for c in my_courses[:6]]

    elif is_student:
        student = request.user.student_profile
        my_enrollments = Enrollment.objects.filter(student=student).select_related('course')
        total_courses = my_enrollments.count()
        total_students = Student.objects.filter(department=student.department).count() if student.department else 1
        total_departments = 1
        
        total_att = Attendance.objects.filter(student=student).count()
        present_att = Attendance.objects.filter(student=student, status='P').count()
        att_pct = round(present_att / total_att * 100, 1) if total_att else 0
        
        recent_students = Student.objects.filter(department=student.department).select_related('user', 'department').exclude(pk=student.pk)[:5]
        recent_results = Result.objects.filter(student=student).select_related('student__user', 'course').order_by('-created_at')[:5]
        
        dept_data = [{'name': student.department.name if student.department else 'N/A', 'count': total_students}]
        course_data = [{'name': en.course.name, 'code': en.course.code, 'count': en.course.enrollments.count()} for en in my_enrollments[:6]]

    else:
        total_students    = Student.objects.count()
        total_courses     = Course.objects.count()
        total_departments = Department.objects.count()

        total_att   = Attendance.objects.count()
        present_att = Attendance.objects.filter(status='P').count()
        att_pct     = round(present_att / total_att * 100, 1) if total_att else 0

        recent_students = Student.objects.select_related('user', 'department').order_by('-created_at')[:5]
        recent_results  = Result.objects.select_related('student__user', 'course').order_by('-created_at')[:5]

        dept_data = [
            {'name': d.name, 'count': d.students.count()}
            for d in Department.objects.all()
        ]

        course_data = [
            {'name': c.name, 'code': c.code, 'count': c.enrollments.count()}
            for c in Course.objects.all()[:6]
        ]

    return render(request, 'dashboard.html', {
        'total_students':    total_students,
        'total_courses':     total_courses,
        'total_departments': total_departments,
        'att_pct':           att_pct,
        'recent_students':   recent_students,
        'recent_results':    recent_results,
        'dept_data':         dept_data,
        'course_data':       course_data,
        'is_teacher':        is_teacher,
        'is_student':        is_student,
    })
