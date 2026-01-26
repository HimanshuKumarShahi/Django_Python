from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.
class Tweet(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    text=models.TextField(max_length=150)
    photo=models.ImageField(upload_to='photos/',blank=True,null=True)
    video=models.FileField(upload_to='videos/',blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def clean(self):
        # Either image or video, not both, not none
        if self.photo and self.video:
            raise ValidationError("Upload either an image or a video, not both.")
        if not self.photo and not self.video:
            raise ValidationError("You must upload either an image or a video.")

    def __str__(self):
        return f'{self.user.username}: {self.text[:15]}...'