from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from accounts.models import CustomUser, Role, Notification, ActivityLog, Teacher
from rest_framework.exceptions import AuthenticationFailed


class TeacherSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if not attrs['phone_number']:
            attrs['phone_number'] = None

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = Teacher(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    class Meta:
        model = Teacher
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'role', 'password', 'confirm_password', 'specialization', 'bio', 'students', 'experience']


class RegisterStep1Serializer(ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    phone_number = serializers.RegexField(
        regex=r'^\+998\d{9}$',
        max_length=13,
        min_length=13,
        error_messages={
            "invalid": "Telefon raqami +998 bilan boshlanishi va jami 13 ta belgidan iborat bo‘lishi kerak."
        }
    )
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ["phone_number", "first_name", "last_name", "password", "confirm_password"]

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Bu telefon raqam orqali allaqachon tizimga ro'yhatdan o'tilgan")
        return value
    
    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Parollar mos kelmadi."})
        return attrs
    

class SMSCodeSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(
        regex=r'^\+998\d{9}$',
        max_length=13,
        min_length=13,
        error_messages={
            "invalid": "Telefon raqami +998 bilan boshlanishi va jami 13 ta belgidan iborat bo‘lishi kerak."
        }
    )
    

class VerifySMSSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(
        regex=r'^\+998\d{9}$',
        max_length=13,
        min_length=13,
        error_messages={
            "invalid": "Telefon raqami +998 bilan boshlanishi va jami 13 ta belgidan iborat bo‘lishi kerak."
        }
    )
    code = serializers.CharField(max_length=6)


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        

class RoleSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = Role
        fields = '__all__'

    def get_name(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.name_ru
        elif lang == 'en':
            return obj.name_en
        return obj.name_uz

class NotificationSerializer(ModelSerializer):
    title = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = '__all__'

    def get_title(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.title_ru
        elif lang == 'en':
            return obj.title_en
        return obj.title_uz
    
    def get_message(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.message_ru
        elif lang == 'en':
            return obj.message_en
        return obj.message_uz


class ActivityLogSerializer(ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'
        

class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'profile_picture', 'role']
        extra_kwargs = {
            'id': {'read_only': True},
            'role': {'read_only': True},
        }
    
    def update(self, instance, validated_data):
        phone_number = validated_data.get('phone_number', instance.phone_number)
        
        if phone_number != instance.phone_number:
            instance.is_verified = False
        
        return super().update(instance, validated_data)