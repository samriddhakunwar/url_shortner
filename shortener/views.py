from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ShortURL
from .permissions import IsOwner
from .serializers import ShortURLSerializer
from .services import create_short_url


class ShortURLViewSet(viewsets.ModelViewSet):
    """CRUD ViewSet for short URLs.

    - All actions require authentication.
    - Users can only access their own URLs (queryset filtering + object permission).
    """

    serializer_class = ShortURLSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ShortURL.objects.none()
        return ShortURL.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a short URL via the service layer.

        Accepts optional `custom_alias` and `expires_at` in the request body.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        short_url = create_short_url(
            user=request.user,
            original_url=serializer.validated_data['original_url'],
            custom_alias=serializer.validated_data.get('custom_alias'),
            expires_at=serializer.validated_data.get('expires_at'),
        )

        output_serializer = self.get_serializer(short_url)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class RedirectView(APIView):
    """Public endpoint: GET /r/<short_code>/

    Resolves a short code, checks expiration, increments analytics, and
    issues an HTTP 302 redirect to the original URL.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request, short_code):
        short_url = get_object_or_404(ShortURL, short_code=short_code)

        # Check expiration
        if short_url.is_expired:
            return Response(
                {'detail': 'This short URL has expired.'},
                status=status.HTTP_410_GONE,
            )

        # Increment analytics atomically
        ShortURL.objects.filter(pk=short_url.pk).update(
            click_count=short_url.click_count + 1,
            last_clicked_at=timezone.now(),
        )

        return redirect(short_url.original_url)
