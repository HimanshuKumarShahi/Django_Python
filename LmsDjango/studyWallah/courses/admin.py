from django.contrib import admin
from .models import Course, Lesson, Question

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')
    inlines = [LessonInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'is_resolved', 'created_at')
    list_filter = ('is_resolved',)