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

from drf_yasg.utils import swagger_auto_schema


class CreateCourseCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(
        operation_description="Add CourseCategory.!",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'name_uz': openapi.Schema(type=openapi.TYPE_STRING, description="add category name in uzbek.!"),
                'name_en': openapi.Schema(type=openapi.TYPE_STRING, description="add category name in english.!"),
                'name_ru': openapi.Schema(type=openapi.TYPE_STRING, description="add category name in russian.!"),
                'description_uz': openapi.Schema(type=openapi.TYPE_STRING, description="add description in uzbek.!"),
                'description_en': openapi.Schema(type=openapi.TYPE_STRING, description="add description in english.!"),
                'description_ru': openapi.Schema(type=openapi.TYPE_STRING, description="add description in russian.!"),
            }
        )
    )
    def post(self, request):
        serializer = CourseCategorySerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class GetCourseCategoryAPIView(APIView):

    @swagger_auto_schema(
        operation_summary="Barcha Categorylarni olish",
        operation_description="Sistemadagi mavjud barcha categorylarni qaytaradi.",
        responses={
            200: openapi.Response(
                description="category ro‘yxati",
                schema=CourseCategorySerializer(many=True)
            ),
            404: openapi.Response(
                description="Hech qanday category topilmadi",

            ),
        }
    )
    def get(self, request):

        try:
            category = CourseCategory.objects.all()
            serializer = CourseCategorySerializer(category, many=True, context={'request': request})
            return Response(serializer.data, status=200)
        except CourseCategory.DoesNotExist:
            return Response({"message": "CourseCategory Not Created Yet.!"}, status=404)


class AddCourseAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    @swagger_auto_schema(
        operation_description="Course Qo'shish.!",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'name_uz': openapi.Schema(type=openapi.TYPE_STRING, description="name kiriting.!"),
                'name_en': openapi.Schema(type=openapi.TYPE_STRING, description="name kiriting.!"),
                'name_ru': openapi.Schema(type=openapi.TYPE_STRING, description="name kiriting.!"),
                'description_uz': openapi.Schema(type=openapi.TYPE_STRING, description="description kiriting.!"),
                'description_en': openapi.Schema(type=openapi.TYPE_STRING, description="description kiriting.!"),
                'description_ru': openapi.Schema(type=openapi.TYPE_STRING, description="description kiriting.!"),
                'price': openapi.Schema(type=openapi.TYPE_NUMBER, format='decimal',
                                        description='Narxni kiriting masalan: 199.99'),
                'banner': openapi.Schema(type=openapi.TYPE_FILE, description="Banner faylni yuklang"),
                'discount': openapi.Schema(type=openapi.TYPE_STRING, description="discount kiriting"),
                'duration': openapi.Schema(type=openapi.TYPE_STRING,
                                           description='davomiyiligini kiritish masalan: 12:45'),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER, description='category kiriting'),
                'instructor': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='instructor kiriting')

            }
        )
    )
    def post(self, request):
        serializer = CourseSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class GetCourseAPIView(APIView):

    @swagger_auto_schema(
        operation_description="course olish",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="Get course.!",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="course",
                schema=CourseSerializer
            ),
            404: "course topilmadi"
        }
    )
    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)

            serializer = CourseSerializer(course, context={'request': request})

            return Response(serializer.data, status=200)

        except Course.DoesNotExist:
            return Response({"error": "course not found.!"}, status=404)


class GetCourseListAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Barcha courselarni olish",
        responses={
            200: openapi.Response(
                description="course ro‘yxati",
                schema=CourseSerializer(many=True)
            ),
            404: openapi.Response(
                description="Hech qanday course topilmadi",

            ),
        }
    )
    def get(self, request):

        try:
            course = Course.objects.all()
            serializer = CourseSerializer(course, many=True, context={'request': request})
            return Response(serializer.data, status=200)
        except Course.DoesNotExist:
            return Response({"message": "Course Not Created Yet.!"}, status=404)