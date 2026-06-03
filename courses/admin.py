from django.contrib import admin
from .models import Course, Enrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'department', 'credits', 'enrolled_count']
    search_fields = ['code', 'name']
    list_filter   = ['department']

    def enrolled_count(self, obj):
        return obj.enrollments.count()
    enrolled_count.short_description = 'Enrolled'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ['student', 'course', 'enrolled_date']
    list_filter   = ['course']
