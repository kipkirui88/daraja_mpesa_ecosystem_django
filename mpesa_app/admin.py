from django.contrib import admin

# Register your models here.
from .models import Payment  # Import your model

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'amount', 'result_code', 'result_description', 'status')