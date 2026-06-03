from django.db import models


class Result(models.Model):
    student       = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='results')
    course        = models.ForeignKey('courses.Course',   on_delete=models.CASCADE, related_name='results')
    marks_obtained= models.FloatField()
    total_marks   = models.FloatField(default=100.0)
    grade         = models.CharField(max_length=3, blank=True)
    exam_date     = models.DateField(null=True, blank=True)
    remarks       = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.roll_number} | {self.course.code} | {self.grade}"

    def calculate_grade(self):
        if not self.total_marks:
            return 'N/A'
        pct = (self.marks_obtained / self.total_marks) * 100
        if pct >= 90: return 'A+'
        if pct >= 80: return 'A'
        if pct >= 70: return 'B+'
        if pct >= 60: return 'B'
        if pct >= 50: return 'C'
        if pct >= 40: return 'D'
        return 'F'

    def save(self, *args, **kwargs):
        self.grade = self.calculate_grade()
        super().save(*args, **kwargs)

    @property
    def percentage(self):
        if not self.total_marks:
            return 0
        return round((self.marks_obtained / self.total_marks) * 100, 1)
