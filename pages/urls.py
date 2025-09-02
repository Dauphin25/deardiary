# Import Django's path function and your home view
from django.urls import path

from pages import views
from pages.views import home_view, page_detail

app_name = 'pages'
# Define URL patterns for the pages app
urlpatterns = [
    path('', home_view, name='home'),
    path('<slug:slug>/', page_detail, name='page_detail'),# '' means the root URL
    path('share-card/<int:question_set_id>/', views.download_share_card, name='share_card'),


]
