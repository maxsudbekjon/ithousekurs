from django.db.models import Q
from django.shortcuts import get_object_or_404

from courses.models import Video, Section, Question
from courses.serializers import VideoSerializer, QuestionSerializer
from courses.utils import build_video_access_map, is_video_test_completed
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response


class AddVideoAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Yangi video yuklash",
        manual_parameters=[
            openapi.Parameter(
                name="video_file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Yuklanadigan video fayl"
            ),
            openapi.Parameter(
                name="title_uz",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="Video sarlavhasi"
            ),
            openapi.Parameter(
                name="title_en",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="Video sarlavhasi"
            ),
            openapi.Parameter(
                name="title_ru",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="Video sarlavhasi"
            ),
            openapi.Parameter(
                name="section",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description="Video tegishli bo‘lgan section nomi (masalan: html)"
            ),
            openapi.Parameter(
                name="duration",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description="Video tavsifi"
            ),
        ],
        consumes=["multipart/form-data"],
        responses={
            201: openapi.Response("Video muvaffaqiyatli yuklandi", VideoSerializer),
            400: "Xato: noto‘g‘ri ma'lumot"
        },
        tags=["Video"]
    )
    def post(self, request):
        section_name = request.data.get('section')
        if not section_name:
            return Response({"error": "section required"}, status=400)

        section = Section.objects.filter(
            Q(title_uz__iexact=section_name) |
            Q(title_en__iexact=section_name) |
            Q(title_ru__iexact=section_name)
        ).first()

        if not section:
            return Response({"error": "Section Not Found.!"},
                            status=404)

        data = request.data.copy()
        data['section'] = section.pk

        serializer = VideoSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class GetVideoAPIView(APIView):
    # permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(
        operation_description="Get all videos in a section",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_PATH,
                description="Section ID (Primary Key)",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Videos in the section",
                schema=VideoSerializer(many=True)
            ),
            404: openapi.Response(
                description="Section videos not found.!"
            ),
        },
        tags=["Video"]
    )
    def get(self, request, pk):
        videos = Video.objects.filter(section_id=pk,is_preview=True)
        if not videos.exists():
            return Response({"error": "Video Not Found.!"},
                            status=404)

        section = videos.first().section
        course = section.course
        access_map = build_video_access_map(request.user, course)
        serializer = VideoSerializer(
            videos,
            many=True,
            context={'request': request, 'access_map': access_map}
        )
        return Response(serializer.data, status=200)


class GetVideoUrlAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get video url by video id with previous test check",
        manual_parameters=[
            openapi.Parameter(
                name="id",
                in_=openapi.IN_PATH,
                description="Video ID (Primary Key)",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Video url or previous video test",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "video_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "video_url": openapi.Schema(type=openapi.TYPE_STRING),
                        "questions": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    }
                )
            ),
            404: openapi.Response(description="Video not found"),
        },
        tags=["Video"]
    )
    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        course_videos = list(
            Video.objects.filter(section__course=video.section.course)
            .order_by('created_at', 'id')
        )
        try:
            current_index = next(
                index for index, item in enumerate(course_videos) if item.id == video.id
            )
        except StopIteration:
            return Response({"error": "Video Not Found.!"},
                            status=404)

        if current_index > 0:
            prev_video = course_videos[current_index - 1]
            if not is_video_test_completed(prev_video):
                questions = Question.objects.filter(video=prev_video)
                serializer = QuestionSerializer(questions, many=True, context={'request': request})
                return Response(
                    {
                        "detail": "Previous video test not completed.",
                        "questions": serializer.data
                    },
                    status=200
                )

        video_url = None
        if video.video_file:
            video_url = request.build_absolute_uri(video.video_file.url)
        return Response(
            {
                "video_id": video.id,
                "video_url": video_url
            },
            status=200
        )
