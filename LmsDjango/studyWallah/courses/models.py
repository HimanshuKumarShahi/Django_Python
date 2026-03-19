from django.db import models
from django.conf import settings

class Course(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    
    CONTENT_CHOICES = [
        ('TEXT', 'Normal Text/Notes'),
        ('PDF', 'Book/PDF'),
        ('IMAGE', 'Infographic/Image'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=10, choices=CONTENT_CHOICES, default='TEXT')
    
    
    text_content = models.TextField(blank=True, null=True) 
    file_content = models.FileField(upload_to='course_files/', blank=True, null=True) 
    image_content = models.ImageField(upload_to='course_images/', blank=True, null=True) 
    
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Question(models.Model):
    """The 'Common Area' for students to ask teachers questions"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField()
    answer = models.TextField(blank=True, null=True) 
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question by {self.user.username} on {self.course.title}"