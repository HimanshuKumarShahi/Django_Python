from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Course, Lesson, Question

# Helper for YouTube Embeds
def get_embed_url(url):
    if not url: return None
    if 'watch?v=' in url: return url.replace('watch?v=', 'embed/')
    if 'youtu.be/' in url: return f"https://www.youtube.com/embed/{url.split('/')[-1]}"
    return url

def course_list(request):
    search_query = request.GET.get('search')
    if search_query:
        courses = Course.objects.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    else:
        courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.students.add(request.user)
    messages.success(request, f"Welcome to {course.title}!")
    return redirect('dashboard') # This name must match urls.py

@login_required
def dashboard(request):
    # This uses the related_name we set in models.py
    my_courses = request.user.enrolled_courses.all() 
    return render(request, 'courses/dashboard.html', {'courses': my_courses})

@login_required
def course_detail(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user not in course.students.all():
        messages.warning(request, "Enroll first to see the lessons!")
        return redirect('course_list')

    lessons = course.lessons.all()
    current_lesson = get_object_or_404(Lesson, id=lesson_id) if lesson_id else lessons.first()

    if current_lesson and current_lesson.content_type == 'VIDEO':
        current_lesson.video_url = get_embed_url(current_lesson.video_url)

    if request.method == "POST":
        query = request.POST.get('query')
        if query:
            Question.objects.create(course=course, user=request.user, query=query)
            messages.success(request, "Question posted!")
            return redirect('lesson_detail', course_id=course.id, lesson_id=current_lesson.id)

    questions = course.discussions.all().order_by('-created_at')
    return render(request, 'courses/course_view.html', {
        'course': course, 'lessons': lessons, 'current_lesson': current_lesson, 'questions': questions
    })