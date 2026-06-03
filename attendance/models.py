from django.db import models


class Attendance(models.Model):
    STATUS_CHOICES = [('P', 'Present'), ('A', 'Absent'), ('L', 'Late')]

    student  = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    course   = models.ForeignKey('courses.Course',   on_delete=models.CASCADE, related_name='attendances')
    date     = models.DateField()
    status   = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    remarks  = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.roll_number} | {self.course.code} | {self.date} | {self.get_status_display()}"
