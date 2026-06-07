from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Result
from .forms import ResultForm
from students.models import Student
from courses.models import Course


@login_required
def result_list(request):
    is_student = hasattr(request.user, 'student_profile')
    is_teacher = hasattr(request.user, 'teacher_profile')

    course_id  = request.GET.get('course_id')
    student_id = request.GET.get('student_id')

    if is_student:
        results = Result.objects.filter(student=request.user.student_profile).select_related('student__user', 'course')
        students = Student.objects.filter(pk=request.user.student_profile.pk).select_related('user')
        courses = Course.objects.filter(enrollments__student=request.user.student_profile)
    elif is_teacher:
        teacher = request.user.teacher_profile
        results = Result.objects.filter(course__teacher=teacher).select_related('student__user', 'course')
        students = Student.objects.filter(enrollments__course__teacher=teacher).select_related('user').distinct()
        courses = Course.objects.filter(teacher=teacher)
    else:
        results  = Result.objects.select_related('student__user', 'course').all()
        students = Student.objects.select_related('user').all()
        courses  = Course.objects.all()

    if course_id:
        results = results.filter(course_id=course_id)
    if student_id and not is_student:
        results = results.filter(student_id=student_id)

    return render(request, 'results/list.html', {
        'results': results, 'students': students, 'courses': courses,
        'sel_course': course_id, 'sel_student': student_id,
        'is_student': is_student,
    })


@login_required
def result_add(request):
    is_admin = request.user.is_staff
    is_teacher = hasattr(request.user, 'teacher_profile')
    if not (is_admin or is_teacher):
        messages.error(request, 'Access denied.')
        return redirect('result_list')

    form = ResultForm(request.POST or None)
    if is_teacher:
        teacher = request.user.teacher_profile
        form.fields['course'].queryset = Course.objects.filter(teacher=teacher)
        form.fields['student'].queryset = Student.objects.filter(enrollments__course__teacher=teacher).distinct()

    if form.is_valid():
        result = form.save(commit=False)
        if is_teacher and (result.course.teacher != request.user.teacher_profile or not Enrollment.objects.filter(course=result.course, student=result.student).exists()):
            messages.error(request, 'Invalid course or student enrollment.')
        else:
            result.save()
            messages.success(request, 'Result added successfully!')
            return redirect('result_list')
    return render(request, 'results/form.html', {'form': form, 'action': 'Add'})


@login_required
def result_edit(request, pk):
    is_admin = request.user.is_staff
    is_teacher = hasattr(request.user, 'teacher_profile')
    if not (is_admin or is_teacher):
        messages.error(request, 'Access denied.')
        return redirect('result_list')

    result = get_object_or_404(Result, pk=pk)

    if is_teacher and result.course.teacher != request.user.teacher_profile:
        messages.error(request, 'Access denied. You cannot edit this result.')
        return redirect('result_list')

    form = ResultForm(request.POST or None, instance=result)
    if is_teacher:
        form.fields['course'].queryset = Course.objects.filter(teacher=request.user.teacher_profile)
        form.fields['student'].queryset = Student.objects.filter(enrollments__course__teacher=request.user.teacher_profile).distinct()

    if form.is_valid():
        form.save()
        messages.success(request, 'Result updated!')
        return redirect('result_list')
    return render(request, 'results/form.html', {'form': form, 'action': 'Edit'})


@login_required
def student_results(request, pk):
    # If the user is a student, restrict them to viewing only their own results.
    if hasattr(request.user, 'student_profile') and request.user.student_profile.pk != pk:
        messages.error(request, 'Access denied. You can only view your own results page.')
        return redirect('student_results', pk=request.user.student_profile.pk)

    student = get_object_or_404(Student, pk=pk)
    results = Result.objects.filter(student=student).select_related('course')
    return render(request, 'results/student_results.html', {
        'student': student, 'results': results
    })
