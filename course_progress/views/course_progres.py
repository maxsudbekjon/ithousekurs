from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from course_progress.serializers import CourseProgressSerializer
from course_progress.models import CourseProgress
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class GetCourseProgresAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_summary="get course_progress",
        operation_description="Berilgan `pk` bo‘yicha course_progress qaytaradi.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="CourseProgress natijasining ID raqami",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response("Course progress topildi", CourseProgressSerializer),
            401: "Avtorizatsiya xatosi",
            404: "Topilmadi"
        }
    )
    def get(self, request, pk):
        try:
            course_progres = CourseProgress.objects.get(pk=pk)
            serializer = CourseProgressSerializer(course_progres)
            return Response(serializer.data, status=200)

        except CourseProgress.DoesNotExist:
            return Response({"message": "not found.!"}, status=404)


class AddCourseProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Add course progress",
        operation_description="add course progress.",
        request_body=CourseProgressSerializer,
        responses={
            201: openapi.Response("Course progress muvaffaqiyatli qo‘shildi", CourseProgressSerializer),
            400: "Yaroqsiz ma’lumot yuborildi",
            401: "Avtorizatsiya xatosi"
        }
    )
    def post(self, request):
        serializer = CourseProgressSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class GetAllCourseProgress(APIView):
    permission_classes = []

    def get(self, request):
        course_progres = CourseProgress.objects.all()
        serializer = CourseProgressSerializer(course_progres, many=True)
        return Response(serializer.data, status=200)
