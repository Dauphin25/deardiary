# Import Django's shortcut to render templates
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from playwright.sync_api import sync_playwright

from diary.models import NewsItem, QuestionSet
from users.models import CustomUser
from .models import Page
from django.db.models import Count
import qrcode
from io import BytesIO
import base64


# Define a view function for the home page


def home_view(request):
    # This function returns the rendered 'home.html' template
    news_items = NewsItem.objects.filter(is_active=True).order_by('display_order', '-created_at')
    # Popular users: count responses grouped by user
    # Leaderboard: count AnswerSessions for each user's QuestionSets
    popular_users = (
        CustomUser.objects.annotate(
            response_count=Count('question_sets__answer_sessions', distinct=True)
        )
        .order_by('-response_count')[:5]
    )
    if request.user.is_authenticated:
        current_qset_count = QuestionSet.objects.filter(owner=request.user).count()
    else:
        current_qset_count = 0

    return render(request, 'home.html',{
        "news_items": news_items,
        "popular_users": popular_users,
        "current_qset_count": current_qset_count
    })
def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_published=True)
    return render(request, 'pages/page_detail.html', {
        'page': page
    })

def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


@login_required(login_url='users:login')
def download_share_card(request, question_set_id):
    question_set = get_object_or_404(QuestionSet, id=question_set_id)
    # Generate QR code linking to answer page
    qr_data_uri = generate_qr_code(request.build_absolute_uri(
        f"/answer/share/{question_set.share_uuid}/"
    ))

    html_content = render_to_string("share_card.html", {
        "question_set": question_set,
        "qr_data_uri": qr_data_uri,
    },
        request=request  # <-- Pass the request here!
                                    )

    # Use Playwright to render HTML to PNG directly
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        image_bytes = page.locator("#share-card").screenshot()
        browser.close()

    response = HttpResponse(image_bytes, content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="{question_set.title}_share_card.png"'
    return response
