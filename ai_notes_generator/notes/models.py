from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class LectureUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    
    media_file = CloudinaryField(
        'media', 
        resource_type='auto',
        folder='AI_notes/media',
        transformation=[
            {'quality': 'auto:eco'},
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class GeneratedNote(models.Model):
    lecture = models.OneToOneField(LectureUpload, on_delete=models.CASCADE, related_name='notes')
    summary_markdown = models.TextField(help_text="Markdown text from Gemini")
    diagram_code = models.TextField(blank=True, null=True, help_text="Mermaid.js code if any")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notes for {self.lecture.title}"