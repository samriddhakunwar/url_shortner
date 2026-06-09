from rest_framework.routers import SimpleRouter

from .views import ShortURLViewSet

router = SimpleRouter()
router.register('urls', ShortURLViewSet, basename='shorturl')

urlpatterns = router.urls
