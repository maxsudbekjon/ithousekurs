from courses.models import Video
from courses.serializers import VideoSerializer
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
                type=openapi.TYPE_INTEGER,
                required=True,
                description="Qaysi section ga tegishli"
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
        serializer = VideoSerializer(data=request.data, context={'request': request})
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
        videos = Video.objects.filter(section_id=pk)
        if not videos.exists():
            return Response({"error": "Video Not Found.!"},
                            status=404)

        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data, status=200)
