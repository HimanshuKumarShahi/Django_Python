from django.contrib import admin
from .models import LectureUpload, GeneratedNote


@admin.register(LectureUpload)
class LectureUploadAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'file_type', 'processing_status', 'is_processed', 'uploaded_at']
    list_filter = ['processing_status', 'file_type', 'is_processed']
    search_fields = ['title', 'user__email']
    readonly_fields = ['uploaded_at']
    ordering = ['-uploaded_at']


@admin.register(GeneratedNote)
class GeneratedNoteAdmin(admin.ModelAdmin):
    list_display = ['lecture', 'ai_model_used', 'word_count', 'concept_count', 'processing_time_seconds', 'created_at']
    search_fields = ['lecture__title']
    readonly_fields = ['created_at', 'updated_at']

    def word_count(self, obj):
        return obj.word_count
    word_count.short_description = 'Words'

    def concept_count(self, obj):
        return obj.concept_count
    concept_count.short_description = 'Concepts'
