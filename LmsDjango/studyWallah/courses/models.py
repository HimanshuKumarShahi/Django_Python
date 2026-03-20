from django.db import models
from django.conf import settings

class Course(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='taught_courses')
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    # This related_name is CRITICAL for the dashboard to work
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_courses', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    CONTENT_CHOICES = [
        ('TEXT', 'Normal Text/Notes'),
        ('PDF', 'Book/PDF'),
        ('IMAGE', 'Infographic/Image'),
        ('VIDEO', 'Video Lesson'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=10, choices=CONTENT_CHOICES, default='TEXT')
    text_content = models.TextField(blank=True, null=True)
    file_content = models.FileField(upload_to='course_files/', blank=True, null=True)
    image_content = models.ImageField(upload_to='course_images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField()
    answer = models.TextField(blank=True, null=True)
    # ADD THIS LINE:
    is_resolved = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question by {self.user.username}"