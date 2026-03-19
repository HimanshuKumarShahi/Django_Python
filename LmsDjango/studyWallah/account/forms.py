from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'mobile_no')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'profile_photo', 'address', 'mobile_no')