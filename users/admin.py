# diary/admin.py
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "actor",
        "type",
        "message",
        "is_read",
        "created_at",
    )
    list_filter = (
        "type",
        "is_read",
        "created_at",
    )
    search_fields = (
        "message",
        "user__username",
        "actor__username",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_editable = ("is_read",)  # allow marking read/unread directly from list view

    fieldsets = (
        (None, {
            "fields": ("user", "actor", "type", "message", "link")
        }),
        ("Status", {
            "fields": ("is_read", "created_at"),
        }),
    )
    readonly_fields = ("created_at",)
