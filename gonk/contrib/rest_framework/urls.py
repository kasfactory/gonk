from rest_framework.routers import DefaultRouter

from gonk.contrib.rest_framework.viewsets import TaskViewSet

router = DefaultRouter(trailing_slash=True)

router.register(r'', TaskViewSet, basename='')

urlpatterns = router.urls
