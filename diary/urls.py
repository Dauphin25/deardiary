from django.urls import path
from . import views

app_name = 'diary'

urlpatterns = [
    path('', views.question_set_list, name='question_set_list'),
    path('create/', views.question_set_create, name='question_set_create'),
    path('my-question-set/<slug:slug>/', views.view_question_set_owner, name='question_set_detail'),
    path('answer/share/<uuid:share_uuid>/', views.answer_shared_question_set, name='answer_question_set_shared'),
    path('my-responses/', views.view_all_responses, name='view_all_responses'),
    path('responses/<slug:slug>/', views.view_responses, name='view_responses'),
    path('response/<int:session_id>/', views.view_single_response, name='view_single_response'),
    path('response/<int:session_id>/download/', views.download_single_response, name='download_single_response'),
    path('question/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:pk>/delete/', views.delete_question, name='delete_question'),
    path('fetch_responses/', views.fetch_responses, name='fetch_responses'),
    path('my-question-set/<slug:slug>/delete/', views.delete_question_set, name='question_set_delete'),
]
