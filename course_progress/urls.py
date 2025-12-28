from django.urls import path
from .views.test_result_views import AddTestResultAPIView, GetTestResultAPIView
from .views.exam_view import ExamListAPIView, ExamDetailAPIView
from .views.course_progres import GetCourseProgresAPIView, AddCourseProgressAPIView, GetAllCourseProgress

urlpatterns = [
    path('add_test_result/', AddTestResultAPIView.as_view(), ),
    path('get_test_result/<int:pk>/', GetTestResultAPIView.as_view(), ),

    path('get_course_progres/<int:pk>/', GetCourseProgresAPIView.as_view(), ),
    path('add_course_progres/', AddCourseProgressAPIView.as_view(), ),
    path('get_course_progress/', GetAllCourseProgress.as_view(), ),

    path('exams/', ExamListAPIView.as_view()),
    path('exams/<int:exam_id>/', ExamDetailAPIView.as_view())
]
