from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from shortener.views import RedirectView

# Swagger schema
schema_view = get_schema_view(
    openapi.Info(
        title='URL Shortener API',
        default_version='v1',
        description='A production-quality URL Shortener REST API with JWT authentication.',
        contact=openapi.Contact(email='contact@urlshortener.local'),
        license=openapi.License(name='MIT'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API
    path('api/', include('accounts.urls')),
    path('api/', include('shortener.urls')),

    # Public redirect
    path('r/<str:short_code>/', RedirectView.as_view(), name='redirect'),

    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
