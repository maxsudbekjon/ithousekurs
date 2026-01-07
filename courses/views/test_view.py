from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models import CourseCategory, Course, Video, Section, VideoComment, Question, \
    Test, Answer
from courses.serializers import CourseCategorySerializer, CourseSerializer, VideoSerializer, \
    SectionSerializer, VideoCommentSerializer, UserSerializer, QuestionSerializer, \
    TestSerializer, AnswerSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AddTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Test Qoshish.!",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'description_uz': openapi.Schema(type=openapi.TYPE_STRING, description="Test matni.!"),
                'description_en': openapi.Schema(type=openapi.TYPE_STRING, description="Test matni.!"),
                'description_ru': openapi.Schema(type=openapi.TYPE_STRING, description="Test matni.!"),
                'title_uz': openapi.Schema(type=openapi.TYPE_STRING, description="title kiriting"),
                'title_en': openapi.Schema(type=openapi.TYPE_STRING, description="title kiriting"),
                'title_ru': openapi.Schema(type=openapi.TYPE_STRING, description="title kiriting"),
                'section': openapi.Schema(type=openapi.TYPE_INTEGER, description='Sectionni ID orqali kiriting.!'),
                'video': openapi.Schema(type=openapi.TYPE_INTEGER, description='Video ID (test har bir video uchun)')
            }
        )
    )
    def post(self, request):
        data = request.data.copy()
        video_id = data.get("video")
        if video_id:
            video = get_object_or_404(Video, pk=video_id)
            if data.get("section") and int(data.get("section")) != video.section_id:
                return Response(
                    {"error": "Video va section mos emas."},
                    status=400
                )
            data["section"] = video.section_id

        serializer = TestSerializer(data=data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


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
