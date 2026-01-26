from django import forms
from .models import Tweet
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['text', 'photo', 'video']
    
    def clean(self):
        cleaned_data = super().clean()
        photo = cleaned_data.get('photo')
        video = cleaned_data.get('video')

        if photo and video:
            raise forms.ValidationError("Choose either image or video.")
        if not photo and not video:
            raise forms.ValidationError("Please upload an image or a video.")

        return cleaned_data



class UserRegistrationForm(UserCreationForm):
    email=forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
