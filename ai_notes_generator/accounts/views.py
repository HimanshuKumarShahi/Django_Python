from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .models import EmailVerificationToken, PasswordResetToken
from .utils import send_verification_email, send_password_reset_email, send_welcome_email


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        full_name = form.cleaned_data['full_name']
        password = form.cleaned_data['password1']

        # Split full_name into first_name / last_name
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Create user (inactive until email verified)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False,  # Requires email verification
        )

        # Create verification token
        token_obj = EmailVerificationToken.objects.create(user=user)

        # Send verification email
        try:
            send_verification_email(user, token_obj.token)
            messages.success(request, f"We've sent a verification link to {email}. Please check your inbox!")
        except Exception as e:
            messages.warning(request, "Account created but email sending failed. Contact support.")

        return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].lower()
        password = form.cleaned_data['password']
        remember_me = form.cleaned_data.get('remember_me', False)

        # Django's username field is email in our case
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, "Please verify your email before logging in. Check your inbox!")
                return render(request, 'accounts/login.html', {'form': form})

            login(request, user)

            # Session expiry based on remember_me
            if not remember_me:
                request.session.set_expiry(0)  # Browser session
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days

            # Set welcome flag for first-time login experience
            is_new_user = not request.session.get('has_logged_in_before', False)
            if is_new_user:
                request.session['show_welcome'] = True
                request.session['has_logged_in_before'] = True

            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "You've been logged out safely. See you soon! 👋")
    return redirect('landing')


def verify_email(request, token):
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)

        if token_obj.is_verified:
            messages.info(request, "Your email is already verified. Please log in.")
            return redirect('login')

        if token_obj.is_expired():
            messages.error(request, "This verification link has expired. Please register again.")
            token_obj.user.delete()
            return redirect('register')

        # Activate user
        user = token_obj.user
        user.is_active = True
        user.save()

        token_obj.is_verified = True
        token_obj.save()

        # Send welcome email
        try:
            send_welcome_email(user)
        except Exception:
            pass

        messages.success(request, "🎉 Email verified! Welcome to AI Notes. Please log in.")
        return render(request, 'accounts/email_verified.html', {'user': user})

    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect('register')


@require_http_methods(["GET", "POST"])
def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].lower()

        try:
            user = User.objects.get(email=email, is_active=True)
            token_obj = PasswordResetToken.objects.create(user=user)
            send_password_reset_email(user, token_obj.token)
        except User.DoesNotExist:
            pass  # Don't reveal whether email exists (security)

        messages.success(request, "If that email is registered, you'll receive a reset link shortly.")
        return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html', {'form': form})


@require_http_methods(["GET", "POST"])
def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token, is_used=False)

        if token_obj.is_expired():
            messages.error(request, "This reset link has expired. Please request a new one.")
            return redirect('forgot_password')

    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid or already used reset link.")
        return redirect('forgot_password')

    form = ResetPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = token_obj.user
        user.set_password(form.cleaned_data['password1'])
        user.save()

        token_obj.is_used = True
        token_obj.save()

        messages.success(request, "✅ Password reset successfully! Please log in with your new password.")
        return redirect('login')

    return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})
