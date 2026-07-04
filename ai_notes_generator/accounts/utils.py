"""
Email utilities for the accounts app.
Handles: verification emails, password reset, welcome emails.
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


def send_verification_email(user, token):
    """Send account verification email."""
    verify_url = f"{settings.SITE_URL}/auth/verify-email/{token}/"
    subject = "✅ Verify your AI Notes account"

    context = {
        'user': user,
        'verify_url': verify_url,
        'site_url': settings.SITE_URL,
    }

    html_content = render_to_string('accounts/emails/verification_email.html', context)
    text_content = f"Hi {user.first_name},\n\nVerify your email by visiting:\n{verify_url}\n\nThis link expires in 24 hours."

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


def send_password_reset_email(user, token):
    """Send password reset email."""
    reset_url = f"{settings.SITE_URL}/auth/reset-password/{token}/"
    subject = "🔐 Reset your AI Notes password"

    context = {
        'user': user,
        'reset_url': reset_url,
        'site_url': settings.SITE_URL,
    }

    html_content = render_to_string('accounts/emails/reset_password_email.html', context)
    text_content = f"Hi {user.first_name},\n\nReset your password:\n{reset_url}\n\nThis link expires in 1 hour."

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


def send_welcome_email(user):
    """Send a welcome email after successful verification."""
    subject = "🎉 Welcome to AI Notes — You're all set!"
    dashboard_url = f"{settings.SITE_URL}/dashboard/"

    context = {
        'user': user,
        'dashboard_url': dashboard_url,
        'site_url': settings.SITE_URL,
    }

    html_content = render_to_string('accounts/emails/welcome_email.html', context)
    text_content = f"Hi {user.first_name}, welcome to AI Notes! Start generating notes at: {dashboard_url}"

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=True)  # Don't block on welcome email
