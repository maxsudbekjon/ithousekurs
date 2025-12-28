from django.db import models
from django.contrib.auth import get_user_model
from courses.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

User = get_user_model()


class Payment(models.Model):
    PAYMENT_METHOD = (
        ('on_time_payment', 'On Time Payment'),
        ('installment', 'Installment'),
    )
    PAYMENT_TYPE = (
        ('click', 'Click'),
        ('paymee', 'Paymee'),
        ('credit_card', 'Credit Card'),
    )
    STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='on_time_payment')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE, default='credit_card')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    invoice_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_url = models.URLField(null=True, blank=True)

    class Meta:
        db_table = 'payment_payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment of {self.amount} for {self.course.name} by {self.user.full_name}"
    

class InstallmentPayment(models.Model):
    INSTALLMENT_COUNT = (
        ( 3, '3 months'),
        ( 6, '6 months'),
        (12, '12 months'),
    )
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='installments')
    installment_count = models.CharField(max_length=20, choices=INSTALLMENT_COUNT, default=3)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateTimeField()
    is_paid = models.BooleanField(default=False)

    class Meta:
        db_table = 'installment_payments'
        verbose_name = 'Installment Payment'
        verbose_name_plural = 'Installment Payments'
        ordering = ['due_date']

    def __str__(self):
        return f"Installment {self.installment_count} of {self.payment.amount} for {self.payment.course.title}"
    

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Payment.STATUS, default='pending')

    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-date']

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.user.full_name} - {self.payment.course.title}"


class CoinTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coin_transactions')
    source = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='coin_transactions')
    coins = models.PositiveIntegerField()
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coin_transactions'
        verbose_name = 'Coin Transaction'
        verbose_name_plural = 'Coin Transactions'
        ordering = ['-time']

    def __str__(self):
        return f"Coin Transaction of {self.coins} coins for {self.user.full_name} - {self.source.title}"

