from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from courses.serializers import AnswerSerializer


class AddAnswerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Javob Qoshish.!",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'question': openapi.Schema(type=openapi.TYPE_INTEGER, description="Savol!"),
                'answer_text_uz': openapi.Schema(type=openapi.TYPE_STRING, description="javob matni.!"),
                'answer_text_en': openapi.Schema(type=openapi.TYPE_STRING, description="javob matni.!"),
                'answer_text_ru': openapi.Schema(type=openapi.TYPE_STRING, description="javob matni.!"),
                'is_correct': openapi.Schema(type=openapi.TYPE_INTEGER,
                                             description='togri yoki notogriligini belgilash True/False')
            }
        )
    )
    def post(self, request):
        serializer = AnswerSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
