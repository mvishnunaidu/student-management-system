from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name        = models.CharField(max_length=100)
    code        = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Student(models.Model):
    YEAR_CHOICES = [
        (1, '1st Year'), (2, '2nd Year'),
        (3, '3rd Year'), (4, '4th Year'),
    ]

    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number  = models.CharField(max_length=20, unique=True)
    department   = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    year         = models.IntegerField(choices=YEAR_CHOICES, default=1)
    phone        = models.CharField(max_length=15, blank=True)
    address      = models.TextField(blank=True)
    date_of_birth= models.DateField(null=True, blank=True)
    profile_pic  = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['roll_number']

    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name() or self.user.username}"

    def get_full_name(self):
        return self.user.get_full_name() or self.user.username

    def attendance_percentage(self):
        from attendance.models import Attendance
        total   = Attendance.objects.filter(student=self).count()
        present = Attendance.objects.filter(student=self, status='P').count()
        return round(present / total * 100, 1) if total else 0
