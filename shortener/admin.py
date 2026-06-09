from django.contrib import admin

from .models import ShortURL


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = (
        'short_code', 'original_url', 'user', 'click_count',
        'last_clicked_at', 'expires_at', 'created_at',
    )
    search_fields = ('short_code', 'original_url')
    list_filter = ('created_at', 'expires_at', 'user')
    readonly_fields = (
        'short_code', 'click_count', 'last_clicked_at',
        'qr_code', 'created_at', 'updated_at',
    )
