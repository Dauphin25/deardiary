# diary/views.py
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import Notification, NotificationType
from .models import QuestionSet, Question, Answer, AnswerSession, QuestionSetStyle
from .forms import QuestionSetCreateForm,  QuestionForm
from django.http import HttpResponseForbidden, Http404
from users.utils import  can_create_qset
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from playwright.sync_api import sync_playwright
from django.template.loader import render_to_string


User = get_user_model()
@login_required(login_url='users:login')
def question_set_create(request):
    if not can_create_qset(request.user):
        messages.error(request, "You’ve reached your question set limit.")
        return redirect('users:profile')

    if request.method == 'POST':
        form = QuestionSetCreateForm(request.POST, user=request.user)
        if form.is_valid():
            selected_style = form.cleaned_data['style']
            if selected_style.is_premium and request.user.userprofile.plan == 'free':
                messages.error(request, "This style is Premium only.")
                return redirect('diary:question_set_create')

            question_set = form.save(commit=False)
            question_set.owner = request.user
            question_set.save()
            request.user.userprofile.save()
            return redirect('diary:question_set_detail', slug=question_set.slug)
    else:
        form = QuestionSetCreateForm(user=request.user)

    return render(request, 'diary/question_set_create.html', {'form': form})

@login_required(login_url='users:login')
def question_set_list(request):
    question_sets = QuestionSet.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'diary/question_set_list.html', {'question_sets': question_sets})


# Shared answering view
@login_required(login_url='users:login')
def answer_shared_question_set(request, share_uuid):
    question_set = get_object_or_404(QuestionSet,  share_uuid=share_uuid)
    questions = question_set.questions.all().order_by('order')
    profile = request.user.userprofile  # or request.user.profile depending on your related_name
    # 🔹 Step 1: Reset weekly answers if a week has passed
    profile.reset_weekly_answers()

    # 🔹 Step 2: Check if user has remaining answers
    if profile.remaining_answers <= 0:
        messages.error(request, "You have reached your weekly answer limit. Please wait for the next week or upgrade to premium.")
        return redirect("users:profile")

    # Prevent owner from answering their own set
    if question_set.owner == request.user:
        return HttpResponseForbidden("You cannot answer your own question set.")

    if request.method == "POST":
        # Create a new AnswerSession
        session = AnswerSession.objects.create(
            respondent=request.user if request.user.is_authenticated else None,
            question_set=question_set
        )

        # Save answers for each question
        for question in questions:
            answer_text = request.POST.get(f"question_{question.id}", "").strip()
            if answer_text:
                Answer.objects.create(
                    session=session,
                    question=question,
                    text=answer_text
                )
        request.user.userprofile.weekly_answer_count += 1
        request.user.userprofile.save()

        # Notify diary owner
        Notification.objects.create(
            user=question_set.owner,
            actor=request.user,
            type=NotificationType.RECEIVED_RESPONSE,
            message=f"{request.user.username} answered your diary '{question_set.title}'.",
            question_set=question_set,  # Use the foreign key instead of `link`
            related_object_id=session.pk,  # Optionally link to the session
        )

        # Notify the answering user (optional confirmation)
        Notification.objects.create(
            user=request.user,
            type=NotificationType.ANSWERED_DIARY,
            message=f"You answered {question_set.owner.username}'s diary '{question_set.title}'.",
            question_set=question_set,
            related_object_id=session.pk,
        )

        return redirect("pages:home")  # or a thank-you page

    # Render template with input fields for each question
    template = question_set.style.template_name if question_set.style else "diary/style_classic.html"

    return render(request, f"diary/{template}", {
        "question_set": question_set,
        "questions": questions,
        "form": None,
        "respondents": None,
        "mode": "answer"
    })

# Owner's view of question set + editing
@login_required(login_url='users:login')
def view_question_set_owner(request, slug):
    question_set = get_object_or_404(QuestionSet, slug = slug, owner=request.user)
    questions = question_set.questions.all()
    form = QuestionForm()

    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            new_q = form.save(commit=False)
            new_q.question_set = question_set
            new_q.save()
            return redirect("diary:question_set_detail", slug = slug)

    respondents = question_set.answer_sessions.all()

    template_name = question_set.style.template_name if question_set.style else "style_classic.html"

    return render(request, f"diary/{template_name}", {
        "question_set": question_set,
        "questions": questions,
        "form": form,
        "respondents": respondents,
        "mode": "owner"
    })



# Owner viewing responses to one question set
@login_required(login_url='users:login')
def view_responses(request, slug):
    question_set = get_object_or_404(QuestionSet, slug=slug, owner=request.user)
    questions = question_set.questions.all()
    sessions = question_set.answer_sessions.all().order_by('-created_at')

    return render(request, "diary/style_grunge.html", {
        "question_set": question_set,
        "questions": questions,
        "form": None,
        "respondents": sessions,
        "mode": "responses"
    })

@login_required(login_url='users:login')
def view_single_response(request, session_id):
    session = (
        AnswerSession.objects.select_related("question_set__style")
        .filter(id=session_id, question_set__owner=request.user)
        .first()
    )
    if not session:
        raise Http404("Answer session not found or access denied")
    # Get answers ordered by the original question order
    questions = session.question_set.questions.all().order_by('order')
    answers = session.answers.select_related('question').order_by('question__order')

    template = session.question_set.style.template_name if session.question_set.style else "diary/style_classic.html"

    return render(request, f"diary/{template}", {
        "question_set": session.question_set,
        "questions": session.question_set.questions.all().order_by('order'),
        "answers": answers,  # <-- pass the queryset here
        "respondent": session.respondent,
        "mode": "view_answers",
        "session": session,  # 👈 This is required
        "is_owner": request.user == session.question_set.owner,  # 👈 here
    })

@login_required(login_url='users:login')
def view_all_responses(request):
    question_sets = request.user.question_sets.prefetch_related('answer_sessions__respondent').all()
    return render(request, 'diary/view_all_responses.html', {
        'question_sets': question_sets
    })


@login_required(login_url='users:login')
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.user != question.question_set.owner:
        return redirect('diary:question_set_detail', slug=question.question_set.slug)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('diary:question_set_detail', slug=question.question_set.slug)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'diary/edit_question.html', {'form': form, 'question': question})

@login_required(login_url='users:login')
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.user == question.question_set.owner:
        question.delete()
    return redirect('diary:question_set_detail', slug=question.question_set.slug)

def style_list(request):
    styles = QuestionSetStyle.objects.all()
    user_plan = request.user.userprofile.plan
    return render(request, 'diary/style_list.html', {
        'styles': styles,
        'user_plan': user_plan
    })


@login_required(login_url='users:login')
def delete_question_set(request, slug):
    qset = get_object_or_404(QuestionSet, slug=slug, owner=request.user)

    if request.method == 'POST':
        qset.delete()
        messages.success(request, "Question Set deleted successfully.")
        return redirect('users:profile')  # or your desired redirect

    return redirect('diary:question_set_detail', slug=slug)  # fallback for non-POST


@login_required(login_url='users:login')
def fetch_responses(request):
    question_sets = QuestionSet.objects.filter(owner=request.user)

    data = []
    for qs in question_sets:
        sessions = qs.answer_sessions.all().order_by('-created_at')
        session_data = []
        for session in sessions:
            session_data.append({
                "id": session.id,
                "respondent": session.respondent.username if session.respondent else "Anonymous",
                "submitted_at": session.created_at.strftime("%b %d, %Y %H:%M"),
                "answers": [
                    {"question": a.question_text, "answer": a.text} for a in session.answers.all()
                ]
            })
        data.append({
            "question_set_id": qs.id,
            "question_set_title": qs.title,
            "responses": session_data
        })

    return JsonResponse({"question_sets": data})


@login_required(login_url='users:login')
def download_single_response(request, session_id):
    session = get_object_or_404(AnswerSession, pk=session_id)
    if session.question_set.owner != request.user:
        raise Http404("Access denied")

    html_content = render_to_string("diary/style_basic.html", {
        "question_set": session.question_set,
        "questions": session.question_set.questions.all().order_by('order'),
        "answers": session.answers.all().order_by('question__order'),
        "respondent": session.respondent,
        "mode": "view_answers",
        "session": session,
        "is_owner": True,
        "request": request,  # <--- pass request so template can build absolute URL
        "pdf_mode": True  # <--- new flag for PDF only styling
    })

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        pdf_bytes = page.pdf(format="A4", print_background=True)
        browser.close()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="{session.question_set.title}.pdf"'
    return response
