from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import StudentListAPIView, CourseListAPIView, AttendanceAPIView, ResultAPIView

urlpatterns = [
    # JWT Token endpoints
    path('token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
    # Data endpoints
    path('students/',      StudentListAPIView.as_view(),  name='api_students'),
    path('courses/',       CourseListAPIView.as_view(),   name='api_courses'),
    path('attendance/',    AttendanceAPIView.as_view(),   name='api_attendance'),
    path('results/',       ResultAPIView.as_view(),       name='api_results'),
]
