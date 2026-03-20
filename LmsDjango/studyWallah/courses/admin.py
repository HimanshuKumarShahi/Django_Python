from django.contrib import admin
from .models import Course, Lesson, Question

# This makes it easy to see questions while looking at a Course
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0 # Don't show empty rows by default

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    # This defines the columns you see in the admin list
    list_display = ('user', 'course', 'is_resolved', 'created_at')
    # This adds a sidebar to filter by resolved status or course
    list_filter = ('is_resolved', 'course')
    # This allows you to search by the student's name or the text of the query
    search_fields = ('user__username', 'query')
    # This allows the teacher to edit the answer directly in the list
    list_editable = ('is_resolved',)

# Update your CourseAdmin to show questions inside the course page
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')
    inlines = [QuestionInline] # Shows questions at the bottom of each course