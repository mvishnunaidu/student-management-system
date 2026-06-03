from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment
from .forms import CourseForm, EnrollmentForm


@login_required
def course_list(request):
    courses = Course.objects.select_related('department').all()
    return render(request, 'courses/list.html', {'courses': courses})


@login_required
def course_add(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('course_list')
    form = CourseForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Course added successfully!')
        return redirect('course_list')
    return render(request, 'courses/form.html', {'form': form, 'action': 'Add'})


@login_required
def course_edit(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('course_list')
    course = get_object_or_404(Course, pk=pk)
    form   = CourseForm(request.POST or None, instance=course)
    if form.is_valid():
        form.save()
        messages.success(request, 'Course updated!')
        return redirect('course_list')
    return render(request, 'courses/form.html', {'form': form, 'action': 'Edit', 'course': course})


@login_required
def course_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('course_list')
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('course_list')
    return render(request, 'courses/confirm_delete.html', {'course': course})


@login_required
def enroll_student(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('course_list')
    course = get_object_or_404(Course, pk=pk)
    form   = EnrollmentForm(request.POST or None)
    if form.is_valid():
        student = form.cleaned_data['student']
        _, created = Enrollment.objects.get_or_create(student=student, course=course)
        if created:
            messages.success(request, f'{student.get_full_name()} enrolled in {course.name}!')
        else:
            messages.warning(request, f'{student.get_full_name()} is already enrolled.')
        return redirect('course_list')
    enrolled = Enrollment.objects.filter(course=course).select_related('student__user')
    return render(request, 'courses/enroll.html', {
        'form': form, 'course': course, 'enrolled': enrolled
    })
