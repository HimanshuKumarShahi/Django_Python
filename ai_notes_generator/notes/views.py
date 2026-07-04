import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST

from .forms import LectureUploadForm
from .models import LectureUpload, GeneratedNote
from .tasks import process_media_and_generate_notes, re_evaluate_notes


def landing(request):
    """Public landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'notes/landing.html')


@login_required
def dashboard(request):
    lectures = LectureUpload.objects.filter(user=request.user).select_related('notes')

    # Stats
    total = lectures.count()
    done = lectures.filter(processing_status='DONE').count()
    processing = lectures.filter(processing_status__in=['PROCESSING', 'PENDING']).count()
    failed = lectures.filter(processing_status='FAILED').count()

    # Welcome modal
    show_welcome = request.session.pop('show_welcome', False)

    return render(request, 'notes/dashboard.html', {
        'lectures': lectures,
        'stats': {'total': total, 'done': done, 'processing': processing, 'failed': failed},
        'show_welcome': show_welcome,
    })


@login_required
def upload_lecture(request):
    form = LectureUploadForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            title = form.cleaned_data['title']
            media_file = form.cleaned_data['media_file']

            # Detect file type
            name_lower = media_file.name.lower()
            video_exts = ['.mp4', '.webm', '.mov', '.avi']
            file_type = 'video' if any(name_lower.endswith(e) for e in video_exts) else 'audio'

            lecture = LectureUpload.objects.create(
                user=request.user,
                title=title,
                media_file=media_file,
                file_type=file_type,
                processing_status='PENDING',
            )

            # Queue Celery task
            process_media_and_generate_notes.delay(lecture.id)

            messages.success(request, f"✅ '{title}' uploaded! AI is now processing your lecture.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")

    return render(request, 'notes/upload.html', {'form': form})


@login_required
def note_detail(request, pk):
    lecture = get_object_or_404(LectureUpload, pk=pk, user=request.user)

    if not lecture.is_processed or not hasattr(lecture, 'notes'):
        messages.info(request, "This lecture is still being processed.")
        return redirect('dashboard')

    note = lecture.notes
    return render(request, 'notes/note_detail.html', {
        'lecture': lecture,
        'note': note,
        'key_concepts': note.key_concepts_json or [],
        'quiz_questions': note.quiz_questions_json or [],
        'skeleton_outline': note.skeleton_outline_json or [],
        'mermaid_code': note.mermaid_diagram or '',
    })


@login_required
def download_pdf(request, pk):
    lecture = get_object_or_404(LectureUpload, pk=pk, user=request.user)
    if not hasattr(lecture, 'notes') or not lecture.notes.pdf_url:
        messages.error(request, "PDF is not available yet.")
        return redirect('dashboard')
    return redirect(lecture.notes.pdf_url)


@login_required
@require_POST
def re_evaluate(request, pk):
    lecture = get_object_or_404(LectureUpload, pk=pk, user=request.user)
    if not hasattr(lecture, 'notes'):
        messages.error(request, "No existing notes to re-evaluate.")
        return redirect('dashboard')

    re_evaluate_notes.delay(lecture.id)
    messages.success(request, f"🔄 Re-evaluation queued for '{lecture.title}'.")
    return redirect('dashboard')

@login_required
@require_POST
def retry_lecture(request, pk):
    lecture = get_object_or_404(LectureUpload, pk=pk, user=request.user)
    lecture.processing_status = 'PENDING'
    lecture.save(update_fields=['processing_status'])
    
    from .tasks import process_media_and_generate_notes
    process_media_and_generate_notes.delay(lecture.id)
    
    messages.success(request, f"🔄 Retrying AI generation for '{lecture.title}'.")
    return redirect('dashboard')

@login_required
def task_status(request, pk):
    """AJAX polling endpoint — returns JSON status of a lecture."""
    lecture = get_object_or_404(LectureUpload, pk=pk, user=request.user)
    data = {
        'status': lecture.processing_status,
        'is_processed': lecture.is_processed,
        'error': lecture.error_message or '',
    }
    if lecture.is_processed and hasattr(lecture, 'notes'):
        data['notes_url'] = f'/notes/{lecture.pk}/'
    return JsonResponse(data)


@login_required
@require_POST
def delete_lecture(request, pk):
    lecture = get_object_or_404(LectureUpload, pk=pk, user=request.user)
    title = lecture.title
    lecture.delete()
    messages.success(request, f"🗑️ '{title}' deleted.")
    return redirect('dashboard')