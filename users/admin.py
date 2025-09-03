# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, UserProfile, Notification
from django.utils.translation import gettext_lazy as _


# --- CustomUser Admin ---
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    # Fields to display in admin list view
    list_display = ('username', 'name', 'surname', 'email', 'gender', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'gender', 'groups')
    search_fields = ('username', 'name', 'surname', 'email', 'city', 'phone_number')
    ordering = ('username',)

    # Group fields in admin detail view
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'surname', 'email', 'city', 'phone_number', 'gender')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Fields when adding a new user via admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'surname', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )


# --- UserProfile Admin ---
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'weekly_answer_count', 'next_reset')
    list_filter = ('plan',)
    search_fields = ('user__username', 'user__name', 'user__surname')
    readonly_fields = ('next_reset',)

    # Optional: reset weekly answers from admin
    actions = ['reset_weekly_answers_action']

    def reset_weekly_answers_action(self, request, queryset):
        for profile in queryset:
            profile.reset_weekly_answers()
        self.message_user(request, "Selected profiles have been reset.")

    reset_weekly_answers_action.short_description = "Reset weekly answers for selected users"


# --- Notification Admin ---
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'actor', 'type', 'message', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')
    search_fields = ('user__username', 'actor__username', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    # Optional: mark notifications as read in bulk
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifications marked as read.")

    mark_as_read.short_description = "Mark selected notifications as read"
