from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Question
from django.contrib.auth.decorators import login_required

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    
    # If no lesson_id is provided, show the first lesson by default
    if lesson_id:
        current_lesson = get_object_or_404(Lesson, id=lesson_id)
    else:
        current_lesson = lessons.first()

    # Handle the "Ask Teacher" form submission
    if request.method == "POST":
        query_text = request.POST.get('query')
        if query_text:
            Question.objects.create(
                course=course, 
                user=request.user, 
                query=query_text
            )
            return redirect('course_detail', course_id=course.id)

    questions = course.discussions.all().order_by('-created_at')

    return render(request, 'courses/course_view.html', {
        'course': course,
        'lessons': lessons,
        'current_lesson': current_lesson,
        'questions': questions
    })

@login_required
def dashboard(request):
    # This assumes you added the 'students' ManyToMany field to the Course model
    my_courses = request.user.enrolled_courses.all() 
    return render(request, 'courses/dashboard.html', {'courses': my_courses})