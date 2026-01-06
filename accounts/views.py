from django.shortcuts import render
from accounts.models import CustomUser, Role, Notification, ActivityLog, Teacher
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework import generics, views
from accounts.serializers import (CustomUserSerializer, ProfileUpdateSerializer,
                                  RoleSerializer, TeacherSerializer,
                                  RegisterStep1Serializer, VerifySMSSerializer,
                                  UserProfileSerializer, ProfileDashboardSerializer
                                  )
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.permissions import IsTeacher
from accounts.utils import generate_verification_code
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserRegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=RegisterStep1Serializer,
        responses={201: RegisterStep1Serializer},
    )
    def post(self, request):
        serializer = RegisterStep1Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification_code = generate_verification_code()

        cache_data = {
            "user_data": serializer.validated_data,
            "code": verification_code
        }

        print(f"Send sms to {serializer.validated_data['phone_number']} code: {verification_code}")
        cache.set(f"verify:{serializer.validated_data['phone_number']}", cache_data, timeout=600)

        return Response({"message": "Tasdiqlash uchun sms kod yuborildi"}, status=status.HTTP_200_OK)


class GetSMSCodeView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "phone_number", openapi.IN_QUERY,
                description="telefon raqam",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: CustomUserSerializer(many=True)}
    )
    def get(self, request):
        phone_number = request.query_params.get("phone_number")

        if not phone_number:
            return Response({"detail": "Telefon raqam kiritilishi kerak"}, status=status.HTTP_400_BAD_REQUEST)
        cache_data = cache.get(f"verify:{phone_number}")
        if cache_data:
            code = cache_data["code"]
            return Response({"detail": f"{phone_number} raqami uchun yuborilgan kod {code}"}, status=status.HTTP_200_OK)

        return Response({"detail": f"{phone_number} raqami uchun SMS kod yuborilmagan yoki eskirgan"},
                        status=status.HTTP_400_BAD_REQUEST)


class VerifySMSAPIView(views.APIView):
    @swagger_auto_schema(
        request_body=VerifySMSSerializer,
        responses={201: VerifySMSSerializer},
    )
    def post(self, request):
        serializer = VerifySMSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        verification_code = serializer.validated_data['code']
        cached_data = cache.get(f"verify:{phone_number}")

        if not cached_data:
            return Response({"detail": "Kod topilmadi yoki muddati o'tib ketgan"}, status=status.HTTP_400_BAD_REQUEST)

        user_data = cached_data["user_data"]
        code = cached_data["code"]

        if code != verification_code:
            return Response({"detail": "Kod notogri"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create(
            phone_number=user_data["phone_number"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            password=make_password(user_data["password"]),
        )

        cache.delete(f"verify:{phone_number}")
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response({
            "detail": "Telefon raqam muvaffaqiyatli tasdiqlandi",
            "data": {
                "refresh": str(refresh),
                "access": access_token
            }
        }, status=status.HTTP_200_OK)


class ResendSMSCodeView(views.APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response({"detail": "Telefon raqam kiritilishi kerak"}, status=status.HTTP_400_BAD_REQUEST)

        verification_code = generate_verification_code()
        cache.set(f"verify:{phone_number}", verification_code, timeout=600)
        print(f"Resend SMS code to {phone_number} code: {verification_code}")

        return Response({"detail": "SMS kod qayta yuborildi"}, status=status.HTTP_200_OK)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_permissions(self):
        if self.http_method_names == ['POST', 'DELETE']:
            self.permission_classes = [permissions.IsAdminUser]
        elif self.http_method_names in ['GET', 'PUT', 'PATCH']:
            self.permission_classes = [IsTeacher]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()


class GetAllUsersView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]
    

class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = {
            "success": True,
            "detail": "Login successful",
        }
        resp = Response(data=data, status=status.HTTP_200_OK)
        resp.set_cookie(
            key='access_token',
            value=response.data['access'],
            httponly=True,
            secure=True,
            samesite='None',
            max_age=15*60
        )
        resp.set_cookie(
            key='refresh_token',
            value=response.data['refresh'],
            httponly=True,
            secure=True,
            samesite='None',
            max_age=7*24*60*60
        )
        return resp
    

class UserProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = self.serializer_class(request.user, data=request.data, context={"request": request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        serializer = self.serializer_class(request.user, data=request.data, context={"request": request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileDashboardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileDashboardSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
class UserProfileUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUpdateSerializer

    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Profil muvaffaqiyatli yangilandi"},
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Profil to‘liq yangilandi"},
            status=status.HTTP_200_OK,
        )