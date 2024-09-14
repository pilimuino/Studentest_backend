from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
    path('documents/<int:pk>/generate_test/', DocumentViewSet.as_view({'post': 'generate_test'}), name='generate_test'),
]

