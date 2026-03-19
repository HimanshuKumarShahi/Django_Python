from django.shortcuts import render
from django.http import HttpResponse
from .models import User

# Create your views here.
def account(request):
    user_list=User.objects.all()
    return render(request,'base.html',{'users':user_list})
