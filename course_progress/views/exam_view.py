from rest_framework import views, status, response
from course_progress.models import Exam
from course_progress.serializers import ExamSerializer
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema


class ExamListAPIView(views.APIView):
    serializer_class = ExamSerializer
    permission_classes = []
    @swagger_auto_schema(
            request_body=ExamSerializer,
            responses={201: ExamSerializer},
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        exam = Exam.objects.all()
        serializer = self.serializer_class(exam, many=True, context={"request": request})
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class ExamDetailAPIView(views.APIView):
    serializer_class = ExamSerializer
    permission_classes = []
    
    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        serializer = self.serializer_class(exam, context={"request": request})
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    @swagger_auto_schema(
            request_body=ExamSerializer,
            responses={201: ExamSerializer},
    )
    def patch(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        serializer = self.serializer_class(exam, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    @swagger_auto_schema(
            request_body=ExamSerializer,
            responses={201: ExamSerializer},
    )
    def put(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        serializer = self.serializer_class(exam, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        exam.delete()
        return response.Response({"message": "Exam successfully deleted"}, status=status.HTTP_200_OK)