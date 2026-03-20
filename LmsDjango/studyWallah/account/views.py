from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect to course_list (the home page for students)
            return redirect('course_list') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'account/register.html', {'form': form})

@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            # Redirect back to settings to show updated data
            return redirect('settings')
    else:
        form = UserProfileForm(instance=request.user)
    
    # FIX: This should render the settings template, NOT course_list
    return render(request, 'account/settings.html', {'form': form})