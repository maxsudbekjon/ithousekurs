from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import PaymeWebhookView, ClickWebhookView
from payment.views import CreateOrderAPIView

urlpatterns = [
    # ...
    path('webhook/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('webhook/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
    path('create-order/', CreateOrderAPIView.as_view(), name='create_order'),
]
