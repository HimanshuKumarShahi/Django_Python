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