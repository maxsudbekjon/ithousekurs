from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from courses.models import CourseCategory, Course, Video, Section, VideoComment
from courses.serializers import CourseCategorySerializer, CourseSerializer, VideoSerializer, \
    SectionSerializer, VideoCommentSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from accounts.models import CustomUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AddSectionAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(
        operation_description="Section Qo'shish.!",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Course qoshish.!"),
                'title_uz': openapi.Schema(type=openapi.TYPE_STRING, description="title kiriting.!"),
                'title_en': openapi.Schema(type=openapi.TYPE_STRING, description="title kiriting.!"),
                'title_ru': openapi.Schema(type=openapi.TYPE_STRING, description="title kiriting.!"),
                'duration': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='davomiyiligini kiritish masalan: 12:45')
            }
        )
    )
    def post(self, request):
        serializer = SectionSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class GetSectionAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Sectionni olish",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="Get Section.!",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Section",
                schema=SectionSerializer
            ),
            404: "Section topilmadi"
        }
    )
    def get(self, request, pk):
        try:
            section = Section.objects.get(pk=pk)
            serializer = SectionSerializer(section, context={'request': request})
            return Response(serializer.data, status=200)
        except Section.DoesNotExist:
            return Response({"error": 'section not found.!'}, status=404)


class GetAllSectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Barcha sectionlarni olish",
        operation_description="Sistemadagi mavjud barcha sectionlarni qaytaradi.",
        responses={
            200: openapi.Response(
                description="Sectionlar ro‘yxati",
                schema=SectionSerializer(many=True)
            ),
            404: openapi.Response(
                description="Hech qanday section topilmadi",

            ),
        }
    )
    def get(self, request):
        sections = Section.objects.all()

        if not sections:
            return Response({"message": "Not Any Section Found.!"}, status=404)
        serializer = SectionSerializer(sections, many=True, context={'request': request})

        return Response(serializer.data, status=200)
