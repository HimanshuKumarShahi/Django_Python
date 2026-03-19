from django.urls import path
from . import views

urlpatterns = [
    # List of all available courses
    path('', views.course_list, name='course_list'),
    
    # The main classroom page (Lessons + Questions)
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    
    # Optional: Direct link to a specific lesson inside a course
    path('<int:course_id>/lesson/<int:lesson_id>/', views.course_detail, name='lesson_detail'),
]