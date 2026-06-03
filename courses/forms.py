from django import forms
from .models import Course, Enrollment
from students.models import Student


class CourseForm(forms.ModelForm):
    class Meta:
        model  = Course
        fields = ['name', 'code', 'description', 'credits', 'department']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'code':        forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'credits':     forms.NumberInput(attrs={'class': 'form-control'}),
            'department':  forms.Select(attrs={'class': 'form-select'}),
        }


class EnrollmentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.select_related('user').all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
