from django.urls import path
from . import views

urlpatterns = [
    path('',                                   views.attendance_select, name='attendance_select'),
    path('mark/<int:course_id>/<str:date_str>/', views.mark_attendance,  name='mark_attendance'),
    path('report/',                             views.attendance_report, name='attendance_report'),
]
