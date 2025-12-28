from rest_framework.views import APIView
from rest_framework.response import Response
from courses.models import ContactUsMessage
from courses.serializers import ContactUsMessageSerializer
from courses.utils import send_telegram
from drf_yasg.utils import swagger_auto_schema


class ContactUsAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Contact Us message yuborish",
        request_body=ContactUsMessageSerializer,
        responses={201: ContactUsMessageSerializer},
    )
    def post(self, request):
        serializer = ContactUsMessageSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        send_telegram(self, instance)
        return Response(serializer.data, status=201)