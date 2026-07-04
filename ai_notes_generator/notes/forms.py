from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings


ALLOWED_AUDIO = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/ogg', 'audio/webm', 'audio/x-m4a']
ALLOWED_VIDEO = ['video/mp4', 'video/webm', 'video/quicktime', 'video/x-msvideo', 'video/mpeg']
ALLOWED_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.ogg', '.mp4', '.webm', '.mov', '.avi']


class LectureUploadForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'E.g., Machine Learning — Lecture 3',
            'class': 'form-input',
            'id': 'id_title',
        })
    )
    media_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'accept': 'audio/*,video/*',
            'class': 'hidden',
            'id': 'id_media_file',
        })
    )

    def clean_media_file(self):
        file = self.cleaned_data.get('media_file')
        if not file:
            raise ValidationError("Please select a file to upload.")

        # Size check
        max_bytes = settings.MAX_UPLOAD_SIZE_BYTES
        if file.size > max_bytes:
            raise ValidationError(
                f"File too large! Max size is {settings.MAX_UPLOAD_SIZE_MB}MB. "
                f"Your file is {file.size // (1024*1024)}MB. "
                f"Tip: Convert to MP3 audio for smaller size."
            )

        if file.size == 0:
            raise ValidationError("The uploaded file is empty.")

        # Extension check
        name_lower = file.name.lower()
        if not any(name_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise ValidationError(
                f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        return file

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 3:
            raise ValidationError("Title must be at least 3 characters.")
        return title