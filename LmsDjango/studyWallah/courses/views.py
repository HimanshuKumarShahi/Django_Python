from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Lesson, Question
from django.db.models import Q

def course_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        courses = Course.objects.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    else:
        courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # This adds the user to the ManyToMany field
    course.students.add(request.user)
    messages.success(request, f"Successfully enrolled in {course.title}!")
    return redirect('dashboard')

@login_required
def dashboard(request):
    # This uses the related_name from your Course model
    my_courses = request.user.enrolled_courses.all() 
    return render(request, 'courses/dashboard.html', {'courses': my_courses})

@login_required
def course_detail(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is actually enrolled
    if request.user not in course.students.all():
        messages.error(request, "Access denied. Please enroll first.")
        return redirect('course_list')

    lessons = course.lessons.all()
    current_lesson = get_object_or_404(Lesson, id=lesson_id) if lesson_id else lessons.first()

    return render(request, 'courses/course_view.html', {
        'course': course,
        'lessons': lessons,
        'current_lesson': current_lesson,
    })