from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from .models import Teacher
from .forms import TeacherForm

@login_required
def teacher_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required to view teachers.')
        return redirect('dashboard')
    
    query = request.GET.get('q', '').strip()
    teachers = Teacher.objects.select_related('user', 'department')
    if query:
        teachers = teachers.filter(
            Q(employee_id__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query)
        )
    return render(request, 'teachers/list.html', {'teachers': teachers, 'query': query})

@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if not request.user.is_staff and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.pk == teacher.pk):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    return render(request, 'teachers/detail.html', {'teacher': teacher})

@login_required
def teacher_add(request):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data.get('email', ''),
                    password=form.cleaned_data.get('password') or 'teacher123',
                )
                teacher = form.save(commit=False)
                teacher.user = user
                teacher.save()
                messages.success(request, f'Teacher {teacher} added successfully!')
                return redirect('teacher_list')
            except IntegrityError:
                form.add_error('username', 'Username already exists. Please choose another.')
    else:
        form = TeacherForm()

    return render(request, 'teachers/form.html', {'form': form, 'action': 'Add'})

@login_required
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if not request.user.is_staff and not (hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.pk == teacher.pk):
        messages.error(request, 'Permission denied.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            user = teacher.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data.get('email', '')
            new_pw = form.cleaned_data.get('password')
            if new_pw:
                user.set_password(new_pw)
            user.save()
            form.save()
            messages.success(request, 'Teacher updated successfully!')
            return redirect('teacher_detail', pk=pk)
    else:
        form = TeacherForm(instance=teacher, initial={
            'first_name': teacher.user.first_name,
            'last_name': teacher.user.last_name,
            'email': teacher.user.email,
            'username': teacher.user.username,
        })

    return render(request, 'teachers/form.html', {'form': form, 'action': 'Edit', 'teacher': teacher})

@login_required
def teacher_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Admin access required.')
        return redirect('dashboard')
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.user.delete()
        messages.success(request, 'Teacher deleted successfully.')
        return redirect('teacher_list')
    return render(request, 'teachers/confirm_delete.html', {'teacher': teacher})
