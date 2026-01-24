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

