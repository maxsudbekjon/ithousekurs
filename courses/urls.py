from django.urls import path
from .views.video_view import *
from .views.course_view import *
from .views.section_view import *
from .views.video_comment_view import *
from .views.question_view import GetQuestionAPIView, GetAllUserAPIView
from .views.test_view import AddAnswerAPIView
from .views.contact_views import ContactUsAPIView

urlpatterns = [
    path('create_category/', CreateCourseCategoryAPIView.as_view(), ),
    path('get_category/', GetCourseCategoryAPIView.as_view(), ),
    path('add_course/', AddCourseAPIView.as_view(), ),
    path('get_all_courses/', GetCourseListAPIView.as_view(), ),
    path('get_course/<int:pk>/', GetCourseAPIView.as_view(), ),
    path('add_video/', AddVideoAPIView.as_view(), ),
    path('get_video/<int:pk>/', GetVideoAPIView.as_view(), ),
    path('add_section/', AddSectionAPIView.as_view(), ),
    path('get_section/<int:pk>/', GetSectionAPIView.as_view(), ),
    path('add_video_comment/<int:pk>/', AddVideoCommentAPIView.as_view(), ),
    path('get_all_video_comments/<int:pk>/', GetAllVideoCommentsAPIView.as_view(), ),
    path('reply_video_comment/<int:pk>/', ReplyCommentToVideoCommentAPIView.as_view(), ),
    path('like_comment/<int:pk>/', LikeVideoCommentAPIView.as_view(), ),
    path('get_question/<int:pk>/', GetQuestionAPIView.as_view(), ),
    path('add_answer/', AddAnswerAPIView.as_view(), ),
    path('get_all_section/', GetAllSectionAPIView.as_view(), ),
    path('get_all_users/', GetAllUserAPIView.as_view(), ),
    path('contact/', ContactUsAPIView.as_view(), ),
]

