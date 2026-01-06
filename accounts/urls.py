from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from rest_framework.routers import DefaultRouter
from django.urls import path
from accounts.views import (UserProfileUpdateView, UserRegisterView, RoleViewSet, TeacherViewSet, UserProfileView,
                            VerifySMSAPIView, GetSMSCodeView, CookieTokenObtainPairView,
                            UserProfileDashboardView
)


router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'teachers', TeacherViewSet, basename='teacher')

urlpatterns = [
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('verify-sms/', VerifySMSAPIView.as_view()),
    path('code/', GetSMSCodeView.as_view(), name='get_sms_code'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/dashboard/', UserProfileDashboardView.as_view(), name='user_profile_dashboard'),
    path("profile/update/", UserProfileUpdateView.as_view(), name="profile_update"),
]


urlpatterns += router.urls
