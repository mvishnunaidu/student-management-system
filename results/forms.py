from django import forms
from .models import Result


class ResultForm(forms.ModelForm):
    class Meta:
        model  = Result
        fields = ['student', 'course', 'marks_obtained', 'total_marks', 'exam_date', 'remarks']
        widgets = {
            'student':        forms.Select(attrs={'class': 'form-select'}),
            'course':         forms.Select(attrs={'class': 'form-select'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}),
            'total_marks':    forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '1'}),
            'exam_date':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks':        forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean(self):
        cleaned = super().clean()
        student = cleaned.get('student')
        course  = cleaned.get('course')
        marks   = cleaned.get('marks_obtained')
        total   = cleaned.get('total_marks')

        # Validate marks don't exceed total
        if marks is not None and total is not None:
            if marks > total:
                raise forms.ValidationError('Marks obtained cannot exceed total marks.')
            if marks < 0:
                raise forms.ValidationError('Marks cannot be negative.')

        # Check unique_together only when creating (not editing)
        if student and course and not self.instance.pk:
            if Result.objects.filter(student=student, course=course).exists():
                raise forms.ValidationError(
                    f'A result for {student} in {course} already exists. Use Edit instead.'
                )
        return cleaned
