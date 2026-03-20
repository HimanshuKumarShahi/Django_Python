from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('settings/', views.profile_settings, name='settings'),

    # Login / Logout
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Password Reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'), 
         name='password_reset'),
]