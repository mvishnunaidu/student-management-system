from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, date
from courses.models import Course, Enrollment
from students.models import Student
from .models import Attendance
from .forms import AttendanceSelectForm


@login_required
def attendance_select(request):
    """Step 1 — pick a course and date."""
    is_admin = request.user.is_staff
    is_teacher = hasattr(request.user, 'teacher_profile')
    if not (is_admin or is_teacher):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AttendanceSelectForm(request.POST)
        if is_teacher:
            form.fields['course'].queryset = request.user.teacher_profile.assigned_courses.all()
        if form.is_valid():
            cid  = form.cleaned_data['course'].id
            dt   = form.cleaned_data['date'].strftime('%Y-%m-%d')
            return redirect('mark_attendance', course_id=cid, date_str=dt)
    else:
        form = AttendanceSelectForm()
        if is_teacher:
            form.fields['course'].queryset = request.user.teacher_profile.assigned_courses.all()
    return render(request, 'attendance/select.html', {'form': form})


@login_required
def mark_attendance(request, course_id, date_str):
    """Step 2 — mark P/A/L for each enrolled student."""
    is_admin = request.user.is_staff
    is_teacher = hasattr(request.user, 'teacher_profile')
    if not (is_admin or is_teacher):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    course = get_object_or_404(Course, pk=course_id)

    # Teachers can only mark attendance for courses assigned to them
    if is_teacher and course.teacher != request.user.teacher_profile:
        messages.error(request, 'Access denied. You are not assigned to teach this course.')
        return redirect('attendance_select')

    att_date    = datetime.strptime(date_str, '%Y-%m-%d').date()
    enrollments = Enrollment.objects.filter(course=course).select_related('student__user')

    if request.method == 'POST':
        for enroll in enrollments:
            student = enroll.student
            status  = request.POST.get(f'status_{student.id}', 'A')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            Attendance.objects.update_or_create(
                student=student, course=course, date=att_date,
                defaults={'status': status, 'remarks': remarks}
            )
        messages.success(request, f'Attendance saved for {course.code} on {att_date}!')
        return redirect('attendance_report')

    existing = {a.student_id: a for a in Attendance.objects.filter(course=course, date=att_date)}
    student_data = []
    for enroll in enrollments:
        s   = enroll.student
        rec = existing.get(s.id)
        student_data.append({
            'student': s,
            'status':  rec.status  if rec else 'P',
            'remarks': rec.remarks if rec else '',
        })

    return render(request, 'attendance/mark.html', {
        'course': course, 'att_date': att_date, 'student_data': student_data,
    })


@login_required
def attendance_report(request):
    student_id = request.GET.get('student_id')
    course_id  = request.GET.get('course_id')

    is_student = hasattr(request.user, 'student_profile')
    is_teacher = hasattr(request.user, 'teacher_profile')

    if is_student:
        # Students can only view their own attendance records
        records = Attendance.objects.filter(student=request.user.student_profile).select_related('student__user', 'course')
        students = Student.objects.filter(pk=request.user.student_profile.pk).select_related('user')
        courses = Course.objects.filter(enrollments__student=request.user.student_profile)
    elif is_teacher:
        # Teachers can only view records for students in their assigned courses
        teacher = request.user.teacher_profile
        records = Attendance.objects.filter(course__teacher=teacher).select_related('student__user', 'course')
        students = Student.objects.filter(enrollments__course__teacher=teacher).select_related('user').distinct()
        courses = Course.objects.filter(teacher=teacher)
    else:
        # Admin can view everything
        records  = Attendance.objects.select_related('student__user', 'course').all()
        students = Student.objects.select_related('user').all()
        courses  = Course.objects.all()

    if student_id and not is_student:
        records = records.filter(student_id=student_id)
    if course_id:
        records = records.filter(course_id=course_id)

    records = records[:200]

    return render(request, 'attendance/report.html', {
        'records': records, 'students': students, 'courses': courses,
        'sel_student': student_id, 'sel_course': course_id,
        'is_student': is_student,
    })
