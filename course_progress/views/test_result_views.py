from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from course_progress.serializers import TestResultSerializer
from course_progress.models import TestResult
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from courses.models import Section, SectionCompletion
from course_progress.models import CourseProgress
from django.utils import timezone


class AddTestResultAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Yangi test natijasi qo‘shish",
        operation_description="Foydalanuvchiga tegishli yangi test natijasi yaratadi.",
        request_body=TestResultSerializer,
        responses={
            201: openapi.Response("Test natijasi muvaffaqiyatli qo‘shildi", TestResultSerializer),
            400: "Yaroqsiz ma’lumot yuborildi",
            401: "Avtorizatsiya xatosi"
        }
    )
    def post(self, request):
        serializer = TestResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            test_result = serializer.save(user=request.user)
            
            if not test_result.is_passed:
                return Response(
                    {
                        "detail": "Testdan o‘tilmadi. Course va section holati o‘zgarmadi."
                    },
                    status=200
                )
            section = test_result.test.section
            
            SectionCompletion.objects.get_or_create(
                user=request.user,
                section=section
            )
            
            course = section.course
            total_section = Section.objects.filter(course=course).count()
            completed_section = SectionCompletion.objects.filter(
                user=request.user,
                section__course=course
            ).count()
            
            if completed_section == total_section:
                course_progress, created = CourseProgress.objects.get_or_create(
                    user=request.user,
                    course=course
                )
                course_progress.is_complete = True
                course_progress.completed_at = timezone.now()
                course_progress.save()
            return Response(serializer.data, status=201)


class GetTestResultAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Bitta test natijasini olish",
        operation_description="Berilgan `pk` bo‘yicha test natijasini qaytaradi.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="Test natijasining ID raqami",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response("Test natijasi topildi", TestResultSerializer),
            401: "Avtorizatsiya xatosi",
            404: "Topilmadi"
        }
    )
    def get(self, request, pk):
        test_result = get_object_or_404(TestResult, pk=pk)
        serializer = TestResultSerializer(test_result)
        return Response(serializer.data, status=200)




