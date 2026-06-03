from django import forms
from courses.models import Course
import datetime


class AttendanceSelectForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.select_related('department').all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date = forms.DateField(
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
