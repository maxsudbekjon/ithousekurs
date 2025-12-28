from django.contrib import admin
from payment.models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'payment_method', 'payment_type', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_type')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
