# Django Project – Complete Setup Guide

This document explains how to set up a Django project from scratch, including virtual environment, project creation, app configuration, static/media handling, and admin setup.

---

## 1️⃣ Environment Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment (Windows):

```bash
.venv\Scripts\activate
```

Install Django:

```bash
pip install django
```

Freeze dependencies (optional but recommended):

```bash
pip freeze > requirements.txt
# OR
pip install -r requirements.txt
```

---

## 2️⃣ Create Django Project

Create a new Django project:

```bash
django-admin startproject Project_Name
```

Move into the project directory:

```bash
cd Project_Name
```

Run the development server:

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/
```

---

## 3️⃣ Create Admin (Superuser)

Create an admin user:

```bash
python manage.py createsuperuser
```

Provide the following details:

* Username
* Email address
* Password

Access Django Admin Panel:

```
http://127.0.0.1:8000/admin/
```

---

## 4️⃣ Static & Media Configuration

### `settings.py`

```python
import os

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## 5️⃣ Project URL Configuration

### `Project_Name/urls.py`

```python
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('your_app_name/',include('App_Name_urls') ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 6️⃣ Create Django App

Create an app inside the project:

```bash
python manage.py startapp App_Name
```

Inside the app folder, ensure these files exist:

* `views.py`
* `urls.py`

---

## 7️⃣ App URLs Configuration

### `App_Name/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
```

---

## 8️⃣ Views Setup

### `App_Name/views.py`

```python
from django.shortcuts import render

# Create your views here
def index(request):
    return render(request, 'index.html')
```

---

## 9️⃣ Register App in Settings

### `settings.py`

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'App_Name',    <--
]
```

---

## 🔟 Templates Configuration

Create a `templates` folder at project root level.

### `settings.py`

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

---
# Links to setup Django: 
 ```
https://docs.chaicode.com/youtube/chai-aur-django/welcome/
 ```
 link: https://docs.chaicode.com/youtube/chai-aur-django/welcome/