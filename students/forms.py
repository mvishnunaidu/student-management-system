from django import forms
from django.contrib.auth.models import User
from .models import Student, Department


class StudentForm(forms.ModelForm):
    # Extra user fields embedded in the same form
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep existing'}
        )
    )

    class Meta:
        model  = Student
        fields = ['roll_number', 'department', 'year', 'phone',
                  'address', 'date_of_birth', 'profile_pic']
        widgets = {
            'roll_number':   forms.TextInput(attrs={'class': 'form-control'}),
            'department':    forms.Select(attrs={'class': 'form-select'}),
            'year':          forms.Select(attrs={'class': 'form-select'}),
            'phone':         forms.TextInput(attrs={'class': 'form-control'}),
            'address':       forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_pic':   forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # When editing an existing student, make username read-only
        if self.instance and self.instance.pk:
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['username'].help_text = 'Username cannot be changed after creation.'

    def clean_username(self):
        """Ensure username is unique — only when creating a new student."""
        username = self.cleaned_data.get('username')
        is_edit  = bool(self.instance and self.instance.pk)
        if not is_edit:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('This username is already taken.')
        return username

    def clean_roll_number(self):
        """Ensure roll number is unique — exclude self when editing."""
        roll = self.cleaned_data.get('roll_number')
        qs   = Student.objects.filter(roll_number=roll)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This roll number is already in use.')
        return roll
