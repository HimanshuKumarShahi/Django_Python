from django.db import models
from django.contrib.auth.models import User


class LectureUpload(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        DONE = 'DONE', 'Done'
        FAILED = 'FAILED', 'Failed'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=255)
    media_file = models.FileField(upload_to='lectures/')
    file_type = models.CharField(max_length=10, default='audio', choices=[('audio', 'Audio'), ('video', 'Video')])
    processing_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"[{self.processing_status}] {self.title}"

    @property
    def status_color(self):
        return {
            'PENDING': 'yellow',
            'PROCESSING': 'blue',
            'DONE': 'green',
            'FAILED': 'red',
        }.get(self.processing_status, 'gray')


class GeneratedNote(models.Model):
    lecture = models.OneToOneField(LectureUpload, on_delete=models.CASCADE, related_name='notes')
    summary_text = models.TextField(blank=True, help_text="Short 2-3 sentence summary")
    summary_markdown = models.TextField(help_text="Full structured Markdown notes from Gemini")
    key_concepts_json = models.JSONField(default=list, blank=True)
    mermaid_diagram = models.TextField(blank=True, null=True, help_text="Mermaid.js diagram code")
    skeleton_outline_json = models.JSONField(default=list, blank=True)
    topic_relationships_json = models.JSONField(default=list, blank=True)
    quiz_questions_json = models.JSONField(default=list, blank=True)
    concept_graph_file = models.ImageField(upload_to='graphs/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    ai_model_used = models.CharField(max_length=100, blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notes for {self.lecture.title}"

    @property
    def word_count(self):
        return len(self.summary_markdown.split()) if self.summary_markdown else 0

    @property
    def concept_count(self):
        return len(self.key_concepts_json) if self.key_concepts_json else 0

    @property
    def quiz_count(self):
        return len(self.quiz_questions_json) if self.quiz_questions_json else 0