from paytechuz.integrations.django.views import BasePaymeWebhookView, BaseClickWebhookView
from payment.models import Payment
from accounts.models import Enrollment
from django.shortcuts import get_object_or_404
from config import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from payment.serializers import PaymentSerializer
from paytechuz.gateways.click import ClickGateway
from paytechuz.gateways.payme import PaymeGateway
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

paymee = PaymeGateway(
    payme_id=settings.PAYTECHUZ['PAYME']['PAYME_ID'],
    payme_key=settings.PAYTECHUZ['PAYME']['PAYME_KEY'],
    is_test_mode=settings.DEBUG
)

click = ClickGateway(
    service_id=settings.PAYTECHUZ['CLICK']['SERVICE_ID'],
    merchant_id=settings.PAYTECHUZ['CLICK']['MERCHANT_ID'],
    merchant_user_id=settings.PAYTECHUZ['CLICK']['MERCHANT_USER_ID'],
    secret_key=settings.PAYTECHUZ['CLICK']['SECRET_KEY'],
    is_test_mode=settings.DEBUG
)


class PaymeWebhookView(BasePaymeWebhookView):
    def successfully_payment(self, params, transaction):
        order = get_object_or_404(Payment, id=transaction.account_id)
        order.status = 'completed'
        order.save()

        Enrollment.objects.get_or_create(
            user=order.user,
            course=order.course,
            defaults={'payment': order}
        )

    def cancelled_payment(self, params, transaction):
        order = get_object_or_404(Payment, id=transaction.account_id)
        order.status = 'cancelled'
        order.save()

class ClickWebhookView(BaseClickWebhookView):
    def successfully_payment(self, params, transaction):
        order = get_object_or_404(Payment, id=transaction.account_id)
        order.status = 'completed'
        order.save()

        Enrollment.objects.get_or_create(
            user=order.user,
            course=order.course,
            defaults={'payment': order}
        )

    def cancelled_payment(self, params, transaction):
        order = get_object_or_404(Payment, id=transaction.account_id)
        order.status = 'cancelled'
        order.save()


class CreateOrderAPIView(APIView):
    serializer_class = PaymentSerializer
    permission_classes = []

    @swagger_auto_schema(
            request_body=PaymentSerializer,
            responses={201: PaymentSerializer},
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(user=request.user)
        payment_url = None

        if payment.payment_type == 'paymee':
            payment_url = paymee.generate_pay_link(
                id=payment.invoice_id,
                amount=payment.amount,
                return_url='https://ithouseonline.uz/uz'
            )
        elif payment.payment_type == 'click':
            payment_url = (
                f"https://my.click.uz/services/pay?"
                f"service_id={settings.PAYTECHUZ['CLICK']['SERVICE_ID']}&"
                f"merchant_id={settings.PAYTECHUZ['CLICK']['MERCHANT_ID']}&"
                f"amount={payment.amount}&"
                f"transaction_param={payment.invoice_id}&"
                f"return_url=https://ithouseonline.uz/uz"
            )
        else:
            return Response({"error": "No'tog'ri tolov turi"}, status=status.HTTP_400_BAD_REQUEST)
        
        payment.payment_url = payment_url
        payment.save(update_fields=["payment_url"])

        response_data = self.serializer_class(payment).data
        response_data['payment_url'] = payment_url

        return Response(response_data, status=status.HTTP_201_CREATED)
