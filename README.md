# Django project : 

## Environment Setup:
 ```Django
python -m venv .venv

.venv\Scripts\activate

 pip install django

 pip install -r requirements.txt  / pip freeze > requirements.txt
 ```
## Start Project
```Django
django-admin startproject Project_Name

cd Project_Name

python manage.py runserver      -># Start the server

```
See on Local Host 8000: http://localhost:8000/

## Create Admin:
```Django
Python manage.py createsuperuser

```
UserName= "Enter Your UserName "
Email address:"Enter Your EmailAddress"
Password: "Create Your PassWord."

Access Admin on localhost 8000: http://localhost:8000/admin/


## Setting.py 
``` python
import os

STATIC_URL = 'static/'
STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```
## Urls.py
``` python

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

```

## creating app in Django
``` python
python manage.py startapp App_Name
```
Using this above command create app. inside the app add "urls.py" & "views.py 👇🏼"

## urls.py
``` python

from . import views
from django.urls import path

urlpatterns = [
    # path('admin/', admin.site.urls),

    path('', views.index,name='index'),

] 
```
## views.py
``` python
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'index.html')
```
Now add your app in "settings.py"
``` python 
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Your App Name',    <-- Here
]

 ## add Dirs =[templates] in "settings.py"
  
'DIRS': [os.path.join(BASE_DIR, 'templates')],
```