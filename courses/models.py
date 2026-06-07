from django.db import models


class Course(models.Model):
    name        = models.CharField(max_length=200)
    code        = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    credits     = models.IntegerField(default=3)
    department  = models.ForeignKey('students.Department', on_delete=models.CASCADE, related_name='courses')
    teacher     = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_courses')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def enrolled_count(self):
        return self.enrollments.count()


class Enrollment(models.Model):
    student       = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='enrollments')
    course        = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_date']

    def __str__(self):
        return f"{self.student} → {self.course}"
