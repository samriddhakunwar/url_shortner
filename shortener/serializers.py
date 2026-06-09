from rest_framework import serializers

from .models import ShortURL


class ShortURLSerializer(serializers.ModelSerializer):
    """Serializer for ShortURL CRUD operations.

    Writable fields: original_url, custom_alias, expires_at
    Read-only fields: id, short_code, short_url, click_count,
                      last_clicked_at, qr_code, created_at, updated_at
    """

    short_url = serializers.SerializerMethodField()
    custom_alias = serializers.CharField(
        max_length=20,
        required=False,
        write_only=True,
        help_text='Optional custom short code. Must be unique.',
    )
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = ShortURL
        fields = (
            'id',
            'original_url',
            'short_code',
            'short_url',
            'custom_alias',
            'click_count',
            'last_clicked_at',
            'expires_at',
            'qr_code_url',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'short_code',
            'short_url',
            'click_count',
            'last_clicked_at',
            'qr_code_url',
            'created_at',
            'updated_at',
        )

    def get_short_url(self, obj):
        """Build the full shortened redirect URL from the request context."""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/r/{obj.short_code}/')
        return f'/r/{obj.short_code}/'

    def get_qr_code_url(self, obj):
        """Return the absolute URL to the QR code image, or null."""
        if obj.qr_code:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code.url)
            return obj.qr_code.url
        return None

    def validate_custom_alias(self, value):
        """Ensure the custom alias is URL-safe and unique."""
        if not value.isalnum():
            raise serializers.ValidationError(
                'Custom alias must contain only letters and numbers.'
            )
        if ShortURL.objects.filter(short_code=value).exists():
            raise serializers.ValidationError(
                f'The alias "{value}" is already taken.'
            )
        return value
