from django.db import models

# Create your models here.
class user(models.Model):
    email=models.EmailField(unique=True)
    mobile_no=models.CharField(max_length=10 , unique=True)