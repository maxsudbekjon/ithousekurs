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
        operation_description="get video",
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
                description="Successfully",
                schema=VideoSerializer()
            ),
            404: openapi.Response(
                description="Video Not Found.!"
            ),
        },
        tags=["Video"]
    )
    def get(self, request, pk):
        try:
            video = Video.objects.get(pk=pk)
            serializer = VideoSerializer(video, context={'request': request})
            return Response(serializer.data, status=200)
        except Video.DoesNotExist:
            return Response({"error": "Video Not Found.!"}, status=404)
