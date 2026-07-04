from celery import shared_task
from .models import LectureUpload, GeneratedNote
import time

@shared_task
def process_media_and_generate_notes(lecture_id):
    try:
        lecture = LectureUpload.objects.get(id=lecture_id)
        
        print(f"Task Started for: {lecture.title}")
        
        media_url = lecture.media_file.url
        print(f"Cloudinary Media URL: {media_url}")
        
        time.sleep(2) 
        
    
        GeneratedNote.objects.create(
            lecture=lecture,
            summary_markdown="# Generated Notes\n\n- Point 1\n- Point 2",
            diagram_code="graph TD;\nA-->B;"
        )
        
        lecture.is_processed = True
        lecture.save()
        
        print("Task Completed Successfully!")
        return "Success"
        
    except Exception as e:
        print(f"Error in task: {e}")
        return "Failed"