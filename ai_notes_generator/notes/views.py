from django.shortcuts import render, redirect
from django.contrib import messages  
from .models import LectureUpload
from .tasks import process_media_and_generate_notes
from django.contrib.auth.models import User

def upload_lecture(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        media_file = request.FILES.get('media_file')

        if media_file:
            max_size = 40 * 1024 * 1024  
            if media_file.size > max_size:
               
                messages.error(request, "File size is too large! Please upload a file under 40 MB.")
                return redirect('upload')
        
        
        user, created = User.objects.get_or_create(username='demo_user')
        
    
        lecture = LectureUpload.objects.create(
            user=user,
            title=title,
            media_file=media_file
        )
        
       
        process_media_and_generate_notes.delay(lecture.id)
        
      
        return redirect('dashboard')
        
    return render(request, 'notes/upload.html')

def dashboard(request):
    lectures = LectureUpload.objects.all().order_by('-uploaded_at')
    return render(request, 'notes/dashboard.html', {'lectures': lectures})