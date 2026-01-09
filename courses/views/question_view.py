from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from courses.models import Answer, Video, Question
from courses.serializers import UserSerializer, QuestionSerializer
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class GetQuestionAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(
        operation_description="get question.!",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="Video ID orqali savollarni olish",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Question",
                schema=QuestionSerializer
            ),
            404: "Question Not Found"
        }
    )
    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        question = Question.objects.filter(video=video)

        if not question.exists():
            return Response({"message": "question not found.!"}, status=404)

        serializer = QuestionSerializer(question, many=True, context={'request': request})

        return Response(serializer.data, status=200)


class GetAllUserAPIView(APIView):
    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True, context={'request': request})

        return Response(serializer.data, status=200)

class CheckAnswerAPIView(APIView):
    def get(self, request, id):
        answer = get_object_or_404(Answer, id=id)
        if answer.is_correct:
            question = answer.question
            if not question.is_completed:
                question.is_completed = True
                question.save(update_fields=["is_completed"])
            return Response({"message": "true"}, status=200)
        return Response({"message": "false"}, status=400)
