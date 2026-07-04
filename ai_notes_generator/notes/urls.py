from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_lecture, name='upload'),
    path('notes/<int:pk>/', views.note_detail, name='note_detail'),
    path('notes/<int:pk>/pdf/', views.download_pdf, name='download_pdf'),
    path('notes/<int:pk>/re-evaluate/', views.re_evaluate, name='re_evaluate'),
    path('notes/<int:pk>/retry/', views.retry_lecture, name='retry_lecture'),
    path('notes/<int:pk>/delete/', views.delete_lecture, name='delete_lecture'),
    path('api/status/<int:pk>/', views.task_status, name='task_status'),
]