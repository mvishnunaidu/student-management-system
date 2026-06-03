from django.contrib import admin
from .models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display  = ['student', 'course', 'marks_obtained', 'total_marks', 'grade', 'percentage']
    list_filter   = ['grade', 'course']
    search_fields = ['student__roll_number', 'student__user__first_name']

    def percentage(self, obj):
        return f"{obj.percentage}%"
