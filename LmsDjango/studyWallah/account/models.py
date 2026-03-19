from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser 

class User(AbstractUser): 
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=10, unique=True)
    profile_photo = models.ImageField(upload_to='profile_photo/', null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile_no']

    def __str__(self):
        return self.email