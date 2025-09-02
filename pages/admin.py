from django.contrib import admin
from .models import Page
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at', 'view_link')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'slug', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'view_link')

    fieldsets = (
        ('Main Info', {
            'fields': ('title', 'slug', 'is_published'),
        }),
        ('Content', {
            'fields': ('content',),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('meta_description',),
            'description': "Optional: Meta description used by search engines.",
        }),
        ('Other', {
            'fields': ('created_at', 'view_link'),
        }),
    )

    def view_link(self, obj):
        if obj.pk:
            url = reverse('pages:page_detail', args=[obj.slug])
            return format_html('<a href="{}" target="_blank">Preview</a>', url)
        return "-"
    view_link.short_description = "Live Preview"
