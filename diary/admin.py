from django.contrib import admin
from .models import QuestionSet, Question, AnswerSession, Answer, QuestionSetStyle, NewsItem

# Inline admin to manage Questions directly inside QuestionSet admin page
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Number of extra empty forms
    ordering = ['order']
    fields = ['order', 'text']

# Admin for QuestionSet with inline questions and useful filters/search
@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'style', 'created_at']
    list_filter = ['style', 'created_at']
    search_fields = ['title', 'owner__username']
    inlines = [QuestionInline]
    ordering = ['-created_at']

# Admin for Question with list display and search
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_set', 'order']
    list_filter = ['question_set']
    search_fields = ['text', 'question_set__title']
    ordering = ['question_set', 'order']

# Inline admin to manage Answers inside AnswerSession admin page
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ['question', 'text']

# Admin for AnswerSession with inline answers and filtering
@admin.register(AnswerSession)
class AnswerSessionAdmin(admin.ModelAdmin):
    list_display = ['respondent', 'question_set', 'created_at']
    list_filter = ['created_at']
    search_fields = ['respondent__username', 'question_set__title']
    inlines = [AnswerInline]
    ordering = ['-created_at']

# Admin for Answer standalone (optional if inline is enough)
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'session', 'text']
    search_fields = ['text', 'question__text']
    ordering = ['session']

@admin.register(QuestionSetStyle)
class QuestionSetStyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_name', 'created_at']
    search_fields = ['name', 'template_name']
    ordering = ['name']



@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ("title", "display_order", "is_active", "created_at")
    list_editable = ("display_order", "is_active")
    ordering = ("display_order", "created_at")
    search_fields = ("title", "description")
    list_filter = ("is_active", "created_at")
    date_hierarchy = "created_at"