from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, mpesa_callback, transaction_list

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('api/mpesa/callback/', mpesa_callback, name='mpesa_callback'),
    path('transactions/', transaction_list, name='transaction_list'),
]
