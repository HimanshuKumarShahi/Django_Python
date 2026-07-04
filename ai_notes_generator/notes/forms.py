from django import forms
from django.core.exceptions import ValidationError
from .models import LectureUpload

class LectureUploadForm(forms.ModelForm):
    class Meta:
        model = LectureUpload
        fields = ['title', 'media_file']

    def clean_media_file(self):
        file = self.cleaned_data.get('media_file')
        if file:
            
            max_size = 40 * 1024 * 1024
            if file.size > max_size:
                raise ValidationError("Cloudinary Free Tier limits uploads to max 40 MB. Please compress your video or upload audio.")
        return file