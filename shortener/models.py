from django.conf import settings
from django.db import models


class ShortURL(models.Model):
    """A shortened URL belonging to an authenticated user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='short_urls',
    )
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=20, unique=True, db_index=True)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    last_clicked_at = models.DateTimeField(blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Short URL'
        verbose_name_plural = 'Short URLs'

    def __str__(self):
        return f'{self.short_code} → {self.original_url[:50]}'

    @property
    def is_expired(self):
        """Check if this short URL has passed its expiration time."""
        if self.expires_at is None:
            return False
        from django.utils import timezone
        return timezone.now() >= self.expires_at
