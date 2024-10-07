from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, mpesa_callback

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('api/mpesa/callback/', mpesa_callback, name='mpesa_callback'),
]
