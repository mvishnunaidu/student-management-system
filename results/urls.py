from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.result_list,     name='result_list'),
    path('add/',                  views.result_add,      name='result_add'),
    path('<int:pk>/edit/',        views.result_edit,     name='result_edit'),
    path('student/<int:pk>/',     views.student_results, name='student_results'),
]
