# Docs for Django.
```
https://docs.chaicode.com/youtube/chai-aur-django/welcome/
```
## link : https://docs.chaicode.com/youtube/chai-aur-django/welcome/


#Important Changes in files:
# settings.py / 
 ```python
   12. import os
   57. 'DIRS': ['templates'],
   119. STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]

 ``` 

# Urls.py / 
```python
    19. from . import views
    21 - 28.  path('admin/', admin.site.urls),
    path('', views.home,name='home'),
    path('about/', views.about,name='about'),
    path('projects/', views.projects,name='projects'),
    path('skills/', views.skills,name='skills'),
    path('contact/', views.contact,name='contact'),
```
# views.py
```python
from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    # return HttpResponse("Hello , World from Himanshu.")
    return render(request,'website/index.html')

def about(request):
    # return HttpResponse("Hello , World from Himanshu. About page")
    return render(request,'website/about.html')

def contact(request):
    # return HttpResponse("Hello , World from Himanshu. Contact page")
    return render(request,'website/contact.html')

def skills(request):
    # return HttpResponse("Hello , World from Himanshu. Skills page")
    return render(request,'website/skills.html')

def projects(request):
    # return HttpResponse("Hello , World from Himanshu. projects page")
    return render(request,'website/projects.html')
```
# And rest of code and file structure
## static / style.css

## templates/Website/ index,about,project,skills,contact.html

#Models.py
```python
from django.db import models
from django.utils import timezone

# Create your models here.
class ChaiVariety(models.Model):
  CHAI_TYPE_CHOICES = [
    ('ML', 'MASALA'),
    ('GR', 'GINGER'),
    ('KL', 'KIWI'),
    ('PL', 'PLAIN'),
    ('EL', 'ELAICHI'),
  ]

  name = models.CharField(max_length=100)
  image = models.ImageField(upload_to='chais/')
  date_added = models.DateTimeField(default=timezone.now)
  type = models.CharField(max_length=2, choices=CHAI_TYPE_CHOICES, default='ML')

  def __str__(self):
    return self.name
```

## using pillow add images in DB.
```python

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    #...
    #...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```