from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Result
from .forms import ResultForm
from students.models import Student
from courses.models import Course


@login_required
def result_list(request):
    course_id  = request.GET.get('course_id')
    student_id = request.GET.get('student_id')
    results  = Result.objects.select_related('student__user', 'course').all()
    students = Student.objects.select_related('user').all()
    courses  = Course.objects.all()
    if course_id:
        results = results.filter(course_id=course_id)
    if student_id:
        results = results.filter(student_id=student_id)
    return render(request, 'results/list.html', {
        'results': results, 'students': students, 'courses': courses,
        'sel_course': course_id, 'sel_student': student_id,
    })


@login_required
def result_add(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('result_list')
    form = ResultForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Result added successfully!')
        return redirect('result_list')
    return render(request, 'results/form.html', {'form': form, 'action': 'Add'})


@login_required
def result_edit(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('result_list')
    result = get_object_or_404(Result, pk=pk)
    form   = ResultForm(request.POST or None, instance=result)
    if form.is_valid():
        form.save()
        messages.success(request, 'Result updated!')
        return redirect('result_list')
    return render(request, 'results/form.html', {'form': form, 'action': 'Edit'})


@login_required
def student_results(request, pk):
    student = get_object_or_404(Student, pk=pk)
    results = Result.objects.filter(student=student).select_related('course')
    return render(request, 'results/student_results.html', {
        'student': student, 'results': results
    })
