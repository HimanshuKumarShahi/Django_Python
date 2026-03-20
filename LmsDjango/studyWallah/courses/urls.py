from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('dashboard/', views.dashboard, name='dashboard'), # <--- Must match Navbar
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/lesson/<int:lesson_id>/', views.course_detail, name='lesson_detail'),
]