"""
AI Notes Generator — Celery Tasks
Full AI pipeline: Gemini audio/video → structured JSON → graph → PDF → Cloudinary
"""
import os
import json
import time
import tempfile
import logging

import requests
import cloudinary.uploader
import redis as redis_lib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

from datetime import date
from celery import shared_task
from django.conf import settings

from google import genai
from google.genai import types

from .models import LectureUpload, GeneratedNote

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def get_redis():
    return redis_lib.Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)


def check_and_increment_quota(model_key: str, daily_limit: int) -> bool:
    """Returns True if quota available; increments counter."""
    r = get_redis()
    today = date.today().isoformat()
    key = f'gemini_quota:{model_key}:{today}'
    current = int(r.get(key) or 0)
    if current >= daily_limit - 2:   # Keep 2-slot buffer
        return False
    r.incr(key)
    r.expire(key, 86400)
    return True


def get_mime_type(filename: str, file_type: str) -> str:
    name = filename.lower()
    if name.endswith('.mp3'):  return 'audio/mpeg'
    if name.endswith('.wav'):  return 'audio/wav'
    if name.endswith('.m4a'):  return 'audio/mp4'
    if name.endswith('.ogg'):  return 'audio/ogg'
    if name.endswith('.webm'): return 'video/webm'
    if name.endswith('.mp4'):  return 'video/mp4'
    if name.endswith('.mov'):  return 'video/quicktime'
    if name.endswith('.avi'):  return 'video/x-msvideo'
    return 'audio/mpeg' if file_type == 'audio' else 'video/mp4'


def download_to_temp(url: str, suffix: str = '.tmp') -> str:
    """Download URL to a local temp file, return path."""
    resp = requests.get(url, stream=True, timeout=180)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    for chunk in resp.iter_content(chunk_size=16384):
        tmp.write(chunk)
    tmp.close()
    return tmp.name


def safe_delete(path: str):
    try:
        if path and os.path.exists(path):
            os.unlink(path)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# CONCEPT GRAPH GENERATOR (matplotlib + networkx)
# ─────────────────────────────────────────────────────────────

def generate_concept_graph(relationships: list, title: str) -> str:
    """Build a dark-themed concept relationship graph. Returns temp PNG path."""
    G = nx.DiGraph()
    for rel in relationships[:18]:
        src = str(rel.get('from', ''))[:30]
        dst = str(rel.get('to', ''))[:30]
        lbl = str(rel.get('relation', ''))[:20]
        if src and dst:
            G.add_edge(src, dst, label=lbl)

    if len(G.nodes) == 0:
        G.add_node("Main Topic")

    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor('#0a0f1e')
    ax.set_facecolor('#0a0f1e')

    # Layout
    if len(G.nodes) > 1:
        try:
            pos = nx.kamada_kawai_layout(G)
        except Exception:
            pos = nx.spring_layout(G, k=2.5, seed=42)
    else:
        pos = {list(G.nodes)[0]: (0, 0)}

    # Node colors based on degree
    degrees = dict(G.degree())
    max_deg = max(degrees.values()) if degrees else 1
    node_colors = [
        f'#{int(99 + 60*(degrees.get(n,0)/max_deg)):02x}{int(102 - 30*(degrees.get(n,0)/max_deg)):02x}f1'
        for n in G.nodes()
    ]

    # Draw
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#4f46e5',
                           arrows=True, arrowsize=18, width=1.8,
                           alpha=0.7, connectionstyle='arc3,rad=0.08',
                           min_source_margin=25, min_target_margin=25)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_color='#1e1b4b',
                           node_size=2800, alpha=0.95,
                           linewidths=2, edgecolors='#6366f1')

    nx.draw_networkx_labels(G, pos, ax=ax, font_color='#e2e8f0',
                            font_size=8, font_weight='bold')

    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True) if d.get('label')}
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=ax,
                                     font_color='#94a3b8', font_size=7,
                                     bbox=dict(alpha=0))

    ax.set_title(f'Concept Map — {title[:60]}', color='#a5b4fc',
                 fontsize=13, fontweight='bold', pad=16)
    ax.axis('off')
    fig.tight_layout()

    tmp_path = tempfile.mktemp(suffix='_graph.png')
    fig.savefig(tmp_path, dpi=150, bbox_inches='tight',
                facecolor='#0a0f1e', edgecolor='none')
    plt.close(fig)
    return tmp_path


# ─────────────────────────────────────────────────────────────
# PDF GENERATOR (ReportLab)
# ─────────────────────────────────────────────────────────────

def generate_pdf(data: dict, graph_path: str, title: str) -> str:
    """Generate a beautiful branded PDF. Returns temp PDF path."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Image, Table, TableStyle, PageBreak,
                                    HRFlowable, KeepTogether)
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from datetime import datetime

    ACCENT   = HexColor('#6366f1')
    ACCENT2  = HexColor('#818cf8')
    DARK_BG  = HexColor('#0f1629')
    CARD     = HexColor('#f8fafc')
    TEXT     = HexColor('#1e293b')
    TEXT2    = HexColor('#475569')
    BORDER   = HexColor('#e2e8f0')

    tmp_pdf = tempfile.mktemp(suffix='_notes.pdf')
    doc = SimpleDocTemplate(tmp_pdf, pagesize=A4,
                            rightMargin=1.8*cm, leftMargin=1.8*cm,
                            topMargin=1.5*cm, bottomMargin=2*cm)

    W = doc.width  # usable width

    def _style(name, **kw):
        s = ParagraphStyle(name, fontName='Helvetica', fontSize=10,
                           textColor=TEXT, spaceAfter=6, leading=15)
        for k, v in kw.items():
            setattr(s, k, v)
        return s

    H1 = _style('H1', fontName='Helvetica-Bold', fontSize=18, textColor=ACCENT, spaceBefore=20, spaceAfter=10)
    H2 = _style('H2', fontName='Helvetica-Bold', fontSize=14, textColor=HexColor('#4f46e5'), spaceBefore=14, spaceAfter=8)
    H3 = _style('H3', fontName='Helvetica-Bold', fontSize=11, textColor=ACCENT2, spaceBefore=10, spaceAfter=6)
    BODY = _style('BODY', alignment=TA_JUSTIFY, spaceAfter=7)
    BULLET = _style('BULLET', leftIndent=18, spaceAfter=4)
    CENTER = _style('CENTER', alignment=TA_CENTER)

    story = []

    # ── COVER PAGE ─────────────────────────────────────────────
    def _cover_row(text_style_pairs, bg, pad=20):
        cells = [[Paragraph(t, s)] for t, s in text_style_pairs]
        tbl = Table([[p[0]] for p in cells], colWidths=[W + 3.6*cm])
        styles_list = [
            ('BACKGROUND', (0, 0), (-1, -1), bg),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), pad),
            ('BOTTOMPADDING', (0, 0), (-1, -1), pad),
            ('LEFTPADDING', (0, 0), (-1, -1), 40),
            ('RIGHTPADDING', (0, 0), (-1, -1), 40),
        ]
        tbl.setStyle(TableStyle(styles_list))
        return tbl

    brand_s = _style('Brand', fontName='Helvetica-Bold', fontSize=16,
                     textColor=white, alignment=TA_CENTER)
    title_s = _style('CTitle', fontName='Helvetica-Bold', fontSize=26,
                     textColor=white, alignment=TA_CENTER, leading=32)
    sum_s   = _style('CSum', fontSize=12, textColor=HexColor('#94a3b8'),
                     alignment=TA_CENTER, leading=18)
    foot_s  = _style('CFoot', fontSize=9, textColor=HexColor('#64748b'),
                     alignment=TA_CENTER)

    story.append(_cover_row([('🧠  AI Notes Generator', brand_s)], DARK_BG, 30))
    story.append(_cover_row([(title[:80], title_s)], DARK_BG, 50))
    story.append(_cover_row([(data.get('summary', '')[:300], sum_s)], DARK_BG, 20))
    story.append(_cover_row(
        [(f'Generated: {datetime.now().strftime("%B %d, %Y")}  •  Model: {data.get("model", "Gemini AI")}', foot_s)],
        DARK_BG, 60))
    story.append(PageBreak())

    # ── KEY CONCEPTS TABLE ──────────────────────────────────────
    concepts = data.get('key_concepts', [])
    if concepts:
        story.append(Paragraph('🧩 Key Concepts', H1))
        story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=12))

        tdata = [[
            Paragraph('<b>Term</b>', _style('TH', fontName='Helvetica-Bold', fontSize=9, textColor=white)),
            Paragraph('<b>Definition</b>', _style('TH2', fontName='Helvetica-Bold', fontSize=9, textColor=white)),
            Paragraph('<b>Priority</b>', _style('TH3', fontName='Helvetica-Bold', fontSize=9, textColor=white)),
        ]]
        imp_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        for c in concepts[:15]:
            imp = c.get('importance', 'medium').lower()
            tdata.append([
                Paragraph(f'<b>{c.get("term","")[:40]}</b>',
                          _style('TC', fontName='Helvetica-Bold', fontSize=9, textColor=ACCENT)),
                Paragraph(c.get('definition', '')[:200],
                          _style('TD', fontSize=9, leading=13)),
                Paragraph(f'{imp_icon.get(imp,"🟡")} {imp.title()}',
                          _style('TI', fontSize=9, textColor=TEXT2)),
            ])

        ct = Table(tdata, colWidths=[3.8*cm, 11*cm, 2.5*cm], repeatRows=1)
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), ACCENT),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [CARD, white]),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(ct)
        story.append(PageBreak())

    # ── FULL NOTES ─────────────────────────────────────────────
    story.append(Paragraph('📝 Full Notes', H1))
    story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=12))

    for line in data.get('notes_markdown', '').split('\n'):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 4))
        elif stripped.startswith('### '):
            story.append(Paragraph(stripped[4:], H3))
        elif stripped.startswith('## '):
            story.append(Paragraph(stripped[3:], H2))
        elif stripped.startswith('# '):
            story.append(Paragraph(stripped[2:], H1))
        elif stripped.startswith(('- ', '* ', '• ')):
            txt = stripped[2:].replace('**','').replace('__','').replace('`', '"')
            story.append(Paragraph(f'• {txt}', BULLET))
        else:
            txt = stripped.replace('**','').replace('__','').replace('`', '"')
            if txt:
                story.append(Paragraph(txt, BODY))

    story.append(PageBreak())

    # ── CONCEPT GRAPH ──────────────────────────────────────────
    if graph_path and os.path.exists(graph_path):
        story.append(Paragraph('🗺️ Concept Map', H1))
        story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=12))
        img = Image(graph_path, width=W, height=W * 0.6)
        story.append(img)
        story.append(Spacer(1, 20))

    # ── SKELETON OUTLINE ───────────────────────────────────────
    outline = data.get('skeleton_outline', [])
    if outline:
        story.append(PageBreak())
        story.append(Paragraph('🧩 Lecture Skeleton', H1))
        story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=12))
        for item in outline[:40]:
            indent = len(item) - len(item.lstrip())
            level = indent // 2
            fs = max(8, 12 - level * 2)
            color = [ACCENT, HexColor('#4f46e5'), ACCENT2, TEXT2][min(level, 3)]
            lpad = level * 16
            s = _style(f'Out{level}', fontSize=fs, textColor=color, leftIndent=lpad, spaceAfter=3)
            story.append(Paragraph(item.strip(), s))

    # ── QUIZ ───────────────────────────────────────────────────
    quizzes = data.get('quiz_questions', [])
    if quizzes:
        story.append(PageBreak())
        story.append(Paragraph('❓ Quiz & Self-Assessment', H1))
        story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=12))
        for i, qa in enumerate(quizzes[:10], 1):
            q_s = _style(f'Q{i}', fontName='Helvetica-Bold', fontSize=10,
                         textColor=HexColor('#1e293b'), spaceBefore=12, spaceAfter=4)
            a_s = _style(f'A{i}', fontSize=9, textColor=TEXT2, leftIndent=12)
            story.append(Paragraph(f'Q{i}. {qa.get("question","")}', q_s))

            ans_tbl = Table([[Paragraph(f'Answer: {qa.get("answer","")}', a_s)]],
                            colWidths=[W])
            ans_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), CARD),
                ('BOX', (0,0), (-1,-1), 0.5, BORDER),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(ans_tbl)

    doc.build(story)
    return tmp_pdf


# ─────────────────────────────────────────────────────────────
# MAIN CELERY TASK
# ─────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=4, default_retry_delay=60,
             name='notes.tasks.process_media_and_generate_notes')
def process_media_and_generate_notes(self, lecture_id: int):
    start = time.time()
    local_media = None
    graph_path  = None
    pdf_path    = None

    try:
        lecture = LectureUpload.objects.get(id=lecture_id)
        lecture.processing_status = 'PROCESSING'
        lecture.error_message = None
        lecture.save(update_fields=['processing_status', 'error_message'])

        # ── 1. Quota check ─────────────────────────────────────
        if not check_and_increment_quota('multimodal', 20):
            lecture.processing_status = 'PENDING'
            lecture.save(update_fields=['processing_status'])
            logger.warning(f"Gemini multimodal quota reached. Retrying lecture {lecture_id} in 5 min.")
            raise self.retry(countdown=300, exc=Exception("Gemini daily quota reached"))

        # ── 2. Init Gemini client ──────────────────────────────
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # ── 3. Download media from Cloudinary ─────────────────
        media_url  = lecture.media_file.url
        mime_type  = get_mime_type(str(lecture.media_file), lecture.file_type)
        suffix     = '.' + mime_type.split('/')[-1].replace('mpeg', 'mp3')
        local_media = download_to_temp(media_url, suffix=suffix)
        logger.info(f"Downloaded media: {os.path.getsize(local_media)} bytes")

        # ── 4. Upload to Gemini File API ──────────────────────
        gemini_file = client.files.upload(
            file=local_media,
            config=types.UploadFileConfig(
                mime_type=mime_type,
                display_name=lecture.title[:100],
            )
        )
        safe_delete(local_media); local_media = None

        # Poll until ACTIVE
        for _ in range(24):  # max 2 minutes
            if gemini_file.state.name == 'ACTIVE':
                break
            if gemini_file.state.name == 'FAILED':
                raise Exception(f"Gemini file upload failed: {gemini_file.state}")
            time.sleep(5)
            gemini_file = client.files.get(name=gemini_file.name)

        if gemini_file.state.name != 'ACTIVE':
            raise Exception("Gemini file did not become ACTIVE within 2 minutes")

        # ── 5. Build mega-prompt ───────────────────────────────
        PROMPT = f"""You are an expert academic notes generator. Analyze this lecture recording titled "{lecture.title}".
Return ONLY valid JSON (no markdown code blocks, no extra text):

{{
  "title": "{lecture.title}",
  "summary": "2-3 sentence executive summary of the entire lecture",
  "notes_markdown": "Full structured notes using ## for sections, ### for subsections, - for bullets. Aim for 600-1500 words.",
  "key_concepts": [
    {{"term": "Concept Name", "definition": "Clear concise definition", "importance": "high"}}
  ],
  "mermaid_diagram": "graph TD\\n    A[Main Topic] --> B[Subtopic 1]\\n    A --> C[Subtopic 2]",
  "skeleton_outline": [
    "# Main Section 1",
    "  ## Subsection 1.1",
    "    ### Point 1.1.1",
    "  ## Subsection 1.2",
    "# Main Section 2"
  ],
  "topic_relationships": [
    {{"from": "Topic A", "to": "Topic B", "relation": "leads to"}}
  ],
  "quiz_questions": [
    {{"question": "What is ...?", "answer": "The answer is ..."}}
  ]
}}

Rules:
- key_concepts: 8-15 concepts, importance must be "high", "medium", or "low"
- mermaid_diagram: valid Mermaid graph TD syntax, max 15 nodes, escape backslashes with \\\\n
- topic_relationships: 6-15 relationships between key concepts
- quiz_questions: 6-10 comprehensive questions covering main topics
- skeleton_outline: 10-25 hierarchical outline items with 2-space indentation per level
"""

        # ── 6. Call Gemini (multimodal model) ─────────────────
        response = client.models.generate_content(
            model=settings.GEMINI_MULTIMODAL_MODEL,
            contents=[gemini_file, PROMPT],
            config=types.GenerateContentConfig(
                temperature=0.25,
                max_output_tokens=8192,
                response_mime_type="application/json",
            )
        )
        # Clean up Gemini file
        try:
            client.files.delete(name=gemini_file.name)
        except Exception:
            pass

        # ── 7. Parse JSON ──────────────────────────────────────
        raw = response.text.strip()
        # Strip any accidental markdown fences
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
            raw = raw.rsplit('```', 1)[0].strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import json_repair
            data = json_repair.loads(raw)

        data['model'] = settings.GEMINI_MULTIMODAL_MODEL

        # ── 8. Generate concept graph (local, no API) ─────────
        rels = data.get('topic_relationships', [])
        graph_url = None
        if rels:
            graph_path = generate_concept_graph(rels, lecture.title)
            g_result = cloudinary.uploader.upload(
                graph_path, folder='AI_notes/graphs', resource_type='image')
            graph_url = g_result['secure_url']

        # ── 9. Generate PDF ────────────────────────────────────
        pdf_path = generate_pdf(data, graph_path, lecture.title)
        p_result = cloudinary.uploader.upload(
            pdf_path, folder='AI_notes/pdfs', resource_type='image')
        pdf_url = p_result['secure_url']

        # ── 10. Save to DB ─────────────────────────────────────
        elapsed = round(time.time() - start, 2)
        GeneratedNote.objects.update_or_create(
            lecture=lecture,
            defaults={
                'summary_text':           data.get('summary', ''),
                'summary_markdown':       data.get('notes_markdown', ''),
                'key_concepts_json':      data.get('key_concepts', []),
                'mermaid_diagram':        data.get('mermaid_diagram', ''),
                'skeleton_outline_json':  data.get('skeleton_outline', []),
                'topic_relationships_json': data.get('topic_relationships', []),
                'quiz_questions_json':    data.get('quiz_questions', []),
                'concept_graph_url':      graph_url or '',
                'pdf_url':                pdf_url,
                'ai_model_used':          settings.GEMINI_MULTIMODAL_MODEL,
                'processing_time_seconds': elapsed,
            }
        )

        lecture.is_processed = True
        lecture.processing_status = 'DONE'
        lecture.save(update_fields=['is_processed', 'processing_status'])

        logger.info(f"✅ Lecture {lecture_id} processed in {elapsed}s")
        return {'status': 'success', 'lecture_id': lecture_id, 'seconds': elapsed}

    except json.JSONDecodeError as e:
        _fail_lecture(lecture_id, f'AI returned invalid JSON: {str(e)[:200]}')
        return {'status': 'failed', 'error': 'json_parse'}

    except Exception as exc:
        err_msg = str(exc)[:400]
        logger.exception(f"Task failed for lecture {lecture_id}: {err_msg}")
        _fail_lecture(lecture_id, err_msg)
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        return {'status': 'failed', 'error': err_msg}

    finally:
        safe_delete(local_media)
        safe_delete(graph_path)
        safe_delete(pdf_path)


def _fail_lecture(lecture_id: int, error: str):
    try:
        lecture = LectureUpload.objects.get(id=lecture_id)
        lecture.processing_status = 'FAILED'
        lecture.error_message = error
        lecture.save(update_fields=['processing_status', 'error_message'])
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# RE-EVALUATE TASK (reuses existing notes, calls text model)
# ─────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3,
             name='notes.tasks.re_evaluate_notes')
def re_evaluate_notes(self, lecture_id: int):
    """Re-process a lecture using the fast text model on existing markdown."""
    start = time.time()
    try:
        lecture = LectureUpload.objects.get(id=lecture_id)
        note = lecture.notes

        lecture.processing_status = 'PROCESSING'
        lecture.is_processed = False
        lecture.save(update_fields=['processing_status', 'is_processed'])

        if not check_and_increment_quota('text_fast', 500):
            lecture.processing_status = 'PENDING'
            lecture.save(update_fields=['processing_status'])
            raise self.retry(countdown=120)

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = f"""You are improving existing lecture notes. 
Here are the existing notes for "{lecture.title}":

{note.summary_markdown[:6000]}

Return ONLY valid JSON (no markdown code blocks):
{{
  "key_concepts": [{{"term":"...","definition":"...","importance":"high|medium|low"}}],
  "mermaid_diagram": "graph TD\\n    A --> B",
  "skeleton_outline": ["# Section 1", "  ## Sub 1.1"],
  "topic_relationships": [{{"from":"A","to":"B","relation":"..."}}],
  "quiz_questions": [{{"question":"...","answer":"..."}}]
}}

Improve and expand on the existing content. Provide 10-15 concepts, 8-10 quiz questions."""

        response = client.models.generate_content(
            model=settings.GEMINI_TEXT_FAST_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3, 
                max_output_tokens=8192,
                response_mime_type="application/json"
            )
        )

        raw = response.text.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1]
            raw = raw.rsplit('```', 1)[0].strip()

        data = json.loads(raw)

        # Regenerate graph + PDF
        graph_path = pdf_path = None
        try:
            rels = data.get('topic_relationships', [])
            graph_url = note.concept_graph_url
            if rels:
                graph_path = generate_concept_graph(rels, lecture.title)
                g = cloudinary.uploader.upload(graph_path, folder='AI_notes/graphs', resource_type='image')
                graph_url = g['secure_url']

            merged_data = {
                'summary': note.summary_text,
                'notes_markdown': note.summary_markdown,
                'key_concepts': data.get('key_concepts', note.key_concepts_json),
                'mermaid_diagram': data.get('mermaid_diagram', note.mermaid_diagram),
                'skeleton_outline': data.get('skeleton_outline', note.skeleton_outline_json),
                'topic_relationships': data.get('topic_relationships', note.topic_relationships_json),
                'quiz_questions': data.get('quiz_questions', note.quiz_questions_json),
                'model': settings.GEMINI_TEXT_FAST_MODEL,
            }
            pdf_path = generate_pdf(merged_data, graph_path, lecture.title)
            p = cloudinary.uploader.upload(pdf_path, folder='AI_notes/pdfs', resource_type='image')
            pdf_url = p['secure_url']

            note.key_concepts_json       = merged_data['key_concepts']
            note.mermaid_diagram         = merged_data['mermaid_diagram']
            note.skeleton_outline_json   = merged_data['skeleton_outline']
            note.topic_relationships_json = merged_data['topic_relationships']
            note.quiz_questions_json     = merged_data['quiz_questions']
            note.concept_graph_url       = graph_url
            note.pdf_url                 = pdf_url
            note.ai_model_used           = settings.GEMINI_TEXT_FAST_MODEL
            note.processing_time_seconds = round(time.time() - start, 2)
            note.save()

        finally:
            safe_delete(graph_path)
            safe_delete(pdf_path)

        lecture.is_processed = True
        lecture.processing_status = 'DONE'
        lecture.save(update_fields=['is_processed', 'processing_status'])

        return {'status': 'success', 'lecture_id': lecture_id}

    except Exception as exc:
        _fail_lecture(lecture_id, str(exc)[:400])
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=exc)
        return {'status': 'failed', 'error': str(exc)}