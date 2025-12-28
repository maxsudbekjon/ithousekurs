from django.shortcuts import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from courses.models import CourseCategory, Course, Video, Section, VideoComment
from courses.serializers import CourseCategorySerializer, CourseSerializer, VideoSerializer, \
    SectionSerializer, VideoCommentSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AddVideoCommentAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Tanlangan videoga yangi comment qo‘shish",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="Comment yoziladigan Video ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(type=openapi.TYPE_STRING, description="Comment matni"),
                'parent_comment': openapi.Schema(type=openapi.TYPE_INTEGER,

                                                 description="Parent comment ID (ixtiyoriy)")
            },
        ),
        responses={
            201: openapi.Response(
                description="Comment muvaffaqiyatli qo‘shildi",
                schema=VideoCommentSerializer()
            ),
            400: "Notog‘ri so‘rov",
            404: "Video topilmadi"
        }
    )
    def post(self, request, pk):
        try:
            video = Video.objects.get(pk=pk)
            serializer = VideoCommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():

                serializer.save(video=video, user=request.user)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        except Video.DoesNotExist:
            return Response({"error": "Video topilmadi"}, status=404)


class GetAllVideoCommentsAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Tanlangan videoga yozilgan barcha asosiy commentlarni olish",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="Commentlarni ko‘rmoqchi bo‘lgan Video ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Video commentlari ro‘yxati",
                schema=VideoCommentSerializer(many=True)
            ),
            404: "Video topilmadi"
        }
    )
    def get(self, request, pk):
        video = get_object_or_404(Video, pk=pk)
        comments = VideoComment.objects.filter(
            video=video,

        )
        serializer = VideoCommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=200)


class ReplyCommentToVideoCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Mavjud commentga reply (javob) yozish",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="Reply yoziladigan Parent Comment ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Reply matni"
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Reply muvaffaqiyatli qo‘shildi",
                schema=VideoCommentSerializer()
            ),
            400: "Notog‘ri so‘rov (validatsiya xatosi)",
            404: "Parent comment topilmadi"
        }
    )
    def post(self, request, pk):
        parent_comment = get_object_or_404(VideoComment, pk=pk)
        serializer = VideoCommentSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(video=parent_comment.video, parent_comment=parent_comment, user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class LikeVideoCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Commentga like yoki unlike qo‘yish. Agar oldin like bosilgan bo‘lsa, "
                              "yana bosilganda unlike bo‘ladi.",
        manual_parameters=[
            openapi.Parameter(
                name='id',
                in_=openapi.IN_PATH,
                description="Like/unlike qilinadigan Comment ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=None,
        responses={
            200: openapi.Response(
                description="Like/unlike javobi",
                examples={
                    "application/json": {"message": "liked"}
                }
            ),
            404: "Comment topilmadi"
        }
    )
    def post(self, request, pk):
        comment = get_object_or_404(VideoComment, pk=pk)

        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            return Response({"message": "like removed"})
        else:
            comment.likes.add(request.user)
            return Response({"message": "liked"})
