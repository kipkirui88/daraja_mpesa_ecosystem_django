from django.db import models

# Create your models here.


class Payment(models.Model):
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    result_code = models.IntegerField(null=True, blank=True)  # Add field for Result Code
    result_description = models.CharField(max_length=255, null=True, blank=True)  # Add field for Result Description
    status = models.CharField(max_length=50, null=True, blank=True)  # Add field for Transaction Status

    def __str__(self):
        return f"Payment {self.phone_number} - {self.amount}"