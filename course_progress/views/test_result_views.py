from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from course_progress.serializers import QuestionResultSerializer
from course_progress.models import QuestionResult
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from courses.models import Section, SectionCompletion, Question, Video
from course_progress.models import CourseProgress
from django.utils import timezone
from rest_framework import status


class AddQuestionResultAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Yangi savol natijasi qo‘shish",
        operation_description="Foydalanuvchiga tegishli yangi savol natijasi yaratadi.",
        request_body=QuestionResultSerializer,
        responses={
            201: openapi.Response("Savol natijasi muvaffaqiyatli qo‘shildi", QuestionResultSerializer),
            400: "Yaroqsiz ma’lumot yuborildi",
            401: "Avtorizatsiya xatosi"
        }
    )
    def post(self, request):
        serializer = QuestionResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            question = serializer.validated_data["question"]
            selected_answer = serializer.validated_data.get("selected_answer")
            if selected_answer and selected_answer.question_id != question.id:
                return Response(
                    {"detail": "Javob savolga tegishli emas."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            is_passed = bool(selected_answer and selected_answer.is_correct)
            question_result, _ = QuestionResult.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={
                    "selected_answer": selected_answer,
                    "is_passed": is_passed
                }
            )

            if not question_result.is_passed:
                return Response(
                    {
                        "detail": "Savolga to‘g‘ri javob berilmadi. Course va section holati o‘zgarmadi."
                    },
                    status=200
                )
            section = question.video.section
            if _is_section_completed(request.user, section):
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
                course_progress, _ = CourseProgress.objects.get_or_create(
                    user=request.user,
                    course=course
                )
                course_progress.is_complete = True
                course_progress.completed = timezone.now()
                course_progress.save()
            response_serializer = QuestionResultSerializer(question_result)
            return Response(response_serializer.data, status=201)


class GetQuestionResultAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Bitta savol natijasini olish",
        operation_description="Berilgan `pk` bo‘yicha savol natijasini qaytaradi.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="Savol natijasining ID raqami",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response("Savol natijasi topildi", QuestionResultSerializer),
            401: "Avtorizatsiya xatosi",
            404: "Topilmadi"
        }
    )
    def get(self, request, pk):
        question_result = get_object_or_404(QuestionResult, pk=pk)
        serializer = QuestionResultSerializer(question_result)
        return Response(serializer.data, status=200)


def _is_section_completed(user, section):
    videos = Video.objects.filter(section=section)
    for video in videos:
        if not _is_video_completed(user, video):
            return False
    return True


def _is_video_completed(user, video):
    total_questions = Question.objects.filter(video=video).count()
    if total_questions == 0:
        return True
    passed_questions = QuestionResult.objects.filter(
        user=user,
        is_passed=True,
        question__video=video
    ).count()
    return passed_questions >= total_questions


