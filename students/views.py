from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from .models import Student, Department
from .forms import StudentForm
from courses.models import Enrollment


@login_required
def student_list(request):
    # If the user is a student, they cannot view the student list directory. Redirect to their own profile page.
    if hasattr(request.user, 'student_profile'):
        return redirect('student_detail', pk=request.user.student_profile.pk)

    query    = request.GET.get('q', '').strip()
    students = Student.objects.select_related('user', 'department')
    if query:
        students = students.filter(
            Q(roll_number__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query)
        )
    return render(request, 'students/list.html', {'students': students, 'query': query})


@login_required
def student_detail(request, pk):
    # If the user is a student, restrict them to viewing only their own details page.
    if hasattr(request.user, 'student_profile') and request.user.student_profile.pk != pk:
        messages.error(request, 'Access denied. You can only view your own profile page.')
        return redirect('student_detail', pk=request.user.student_profile.pk)

    student     = get_object_or_404(Student, pk=pk)
    enrollments = Enrollment.objects.filter(student=student).select_related('course__department')
    from results.models import Result
    from attendance.models import Attendance
    results     = Result.objects.filter(student=student).select_related('course')
    att_total   = Attendance.objects.filter(student=student).count()
    att_present = Attendance.objects.filter(student=student, status='P').count()
    att_pct     = round(att_present / att_total * 100, 1) if att_total else 0
    return render(request, 'students/detail.html', {
        'student': student, 'enrollments': enrollments,
        'results': results,  'att_pct': att_pct,
    })


@login_required
def student_add(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('student_list')

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create the Django User first
                user = User.objects.create_user(
                    username   = form.cleaned_data['username'],
                    first_name = form.cleaned_data['first_name'],
                    last_name  = form.cleaned_data['last_name'],
                    email      = form.cleaned_data.get('email', ''),
                    password   = form.cleaned_data.get('password') or 'student123',
                )
                # Link to Student profile
                student = form.save(commit=False)
                student.user = user
                student.save()
                messages.success(request, f'Student {student} added successfully!')
                return redirect('student_list')
            except IntegrityError:
                form.add_error('username', 'Username already exists. Please choose another.')
    else:
        form = StudentForm()

    return render(request, 'students/form.html', {'form': form, 'action': 'Add'})


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # Only admin or the student themselves can edit
    if not request.user.is_staff and request.user != student.user:
        messages.error(request, 'Permission denied.')
        return redirect('student_list')

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            # Update the linked User record
            user = student.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name  = form.cleaned_data['last_name']
            user.email      = form.cleaned_data.get('email', '')
            new_pw = form.cleaned_data.get('password')
            if new_pw:
                user.set_password(new_pw)
            user.save()
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('student_detail', pk=pk)
    else:
        form = StudentForm(instance=student, initial={
            'first_name': student.user.first_name,
            'last_name':  student.user.last_name,
            'email':      student.user.email,
            'username':   student.user.username,
        })

    return render(request, 'students/form.html', {
        'form': form, 'action': 'Edit', 'student': student
    })


@login_required
def student_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('student_list')
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.user.delete()   # CASCADE deletes Student too
        messages.success(request, 'Student deleted successfully.')
        return redirect('student_list')
    return render(request, 'students/confirm_delete.html', {'student': student})
