from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'John Doe',
            'class': 'auth-input',
            'id': 'id_full_name',
            'autocomplete': 'name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com',
            'class': 'auth-input',
            'id': 'id_email',
            'autocomplete': 'email',
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Min. 8 characters',
            'class': 'auth-input',
            'id': 'id_password1',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repeat your password',
            'class': 'auth-input',
            'id': 'id_password2',
            'autocomplete': 'new-password',
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError({'password2': 'Passwords do not match.'})
        if p1:
            try:
                validate_password(p1)
            except ValidationError as e:
                raise ValidationError({'password1': list(e.messages)})
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com',
            'class': 'auth-input',
            'id': 'id_login_email',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Your password',
            'class': 'auth-input',
            'id': 'id_login_password',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(required=False)


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com',
            'class': 'auth-input',
            'id': 'id_forgot_email',
        })
    )


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New password',
            'class': 'auth-input',
            'id': 'id_new_password1',
        })
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repeat new password',
            'class': 'auth-input',
            'id': 'id_new_password2',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError({'password2': 'Passwords do not match.'})
        if p1:
            try:
                validate_password(p1)
            except ValidationError as e:
                raise ValidationError({'password1': list(e.messages)})
        return cleaned_data
