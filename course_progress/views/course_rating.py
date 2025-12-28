from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from course_progress.serializers import CourseRatingSerializer
from course_progress.models import CourseRating
from drf_yasg.utils import swagger_auto_schema
from accounts.models import Enrollment


class CourseRatingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Kurs baholash",
        operation_description="Foydalanuvchi kursni baholaydi yoki mavjud bahosini yangilaydi.",
        request_body=CourseRatingSerializer,
        responses={
            200: "Kurs bahosi muvaffaqiyatli qo‘shildi yoki yangilandi",
            400: "Yaroqsiz ma’lumot yuborildi",
            401: "Avtorizatsiya xatosi"
        }
    )
    def post(self, request):
        serializer = CourseRatingSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            course_id = serializer.validated_data['course'].id
            user = request.user
            rating_value = serializer.validated_data['rating']
            enrollment = Enrollment.objects.filter(user=user, course_id=course_id).first()

            if enrollment:
                rating = CourseRating.objects.filter(user=user, course_id=course_id).first()
                if not rating:
                    rating = CourseRating(user=user, course_id=course_id)
                    rating.rating = rating_value
                    rating.save()
                    return Response({"message": "Kurs bahosi muvaffaqiyatli qo‘shildi"}, status=200)
                else:
                    return Response({"message": "Siz allaqachon ushbu kursni baholagansiz"}, status=400)
                
            else:
                return Response({"error": "Foydalanuvchi ushbu kursga yozilmagan"}, status=400)

        return Response(serializer.errors, status=400)