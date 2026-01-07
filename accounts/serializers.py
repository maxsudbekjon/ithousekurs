from datetime import timedelta

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from accounts.models import CustomUser, Role, Notification, ActivityLog, Teacher, Enrollment
from course_progress.models import CourseProgress
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
        fields = ["id",'first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 'role', 'password', 'confirm_password', 'specialization', 'bio', 'students', 'experience']


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


class ProfileDashboardSerializer(serializers.Serializer):
    """
    Aggregates profile data for the dashboard (stats, weekly activity, achievements).
    """

    XP_PER_LEVEL = 250

    user = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    weekly_activity = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()
    recent_activity = serializers.SerializerMethodField()
    summary_cards = serializers.SerializerMethodField()

    # region: helpers
    def _lang(self):
        request = self.context.get("request")
        return getattr(request, "LANGUAGE_CODE", "uz") if request else "uz"

    def _course_title(self, course):
        lang = self._lang()
        if lang == "ru":
            return course.name_ru
        if lang == "en":
            return course.name_en
        return course.name_uz

    def _basic_counts(self, user):
        if hasattr(self, "_basic_counts_cache"):
            return self._basic_counts_cache

        completed_courses = Enrollment.objects.filter(user=user, is_completed=True).count()
        active_courses = Enrollment.objects.filter(user=user, is_completed=False).count()
        completed_lessons_qs = CourseProgress.objects.filter(
            user=user,
            is_complete=True,
            completed__isnull=False,
        )
        completed_lessons = completed_lessons_qs.count()
        self._basic_counts_cache = {
            "completed_courses": completed_courses,
            "active_courses": active_courses,
            "completed_lessons": completed_lessons,
            "completed_lessons_qs": completed_lessons_qs,
        }
        return self._basic_counts_cache

    def _streak_info(self, user):
        if hasattr(self, "_streak_cache"):
            return self._streak_cache

        completion_dates = set(
            CourseProgress.objects.filter(
                user=user,
                is_complete=True,
                completed__isnull=False,
            ).values_list("completed__date", flat=True)
        )

        today = timezone.localdate()
        current_streak = 0
        cursor = today
        while cursor in completion_dates:
            current_streak += 1
            cursor -= timedelta(days=1)

        best_streak = 0
        prev_date = None
        rolling = 0
        for date in sorted(completion_dates):
            if prev_date and date == prev_date + timedelta(days=1):
                rolling += 1
            else:
                rolling = 1
            best_streak = max(best_streak, rolling)
            prev_date = date

        self._streak_cache = {
            "current": current_streak,
            "best": best_streak,
            "dates": completion_dates,
        }
        return self._streak_cache

    # endregion

    def get_user(self, obj):
        request = self.context.get("request")
        avatar_url = None
        if obj.profile_picture and request:
            avatar_url = request.build_absolute_uri(obj.profile_picture.url)
        return {
            "id": str(obj.id),
            "full_name": obj.full_name,
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "phone_number": obj.phone_number,
            "email": obj.email,
            "location": obj.location,
            "avatar": avatar_url,
            "member_since": obj.created_at.date() if obj.created_at else None,
            "role": obj.role.name_uz if obj.role else None,
        }

    def get_stats(self, obj):
        counts = self._basic_counts(obj)
        streak = self._streak_info(obj)
        xp = obj.rating or 0
        level = max(1, xp // self.XP_PER_LEVEL + 1)
        next_level_xp = (level + 1) * self.XP_PER_LEVEL if xp else self.XP_PER_LEVEL
        return {
            "xp": xp,
            "level": level,
            "next_level_xp": next_level_xp,
            "xp_to_next_level": max(next_level_xp - xp, 0),
            "completed_courses": counts["completed_courses"],
            "active_courses": counts["active_courses"],
            "completed_lessons": counts["completed_lessons"],
            "streak_current": streak["current"],
            "streak_best": streak["best"],
        }

    def get_weekly_activity(self, obj):
        today = timezone.localdate()
        start_date = today - timedelta(days=6)
        base_qs = (
            CourseProgress.objects.filter(
                user=obj,
                is_complete=True,
                completed__date__gte=start_date,
                completed__date__lte=today,
            )
            .annotate(day=TruncDate("completed"))
            .values("day")
            .annotate(count=Count("id"))
        )
        day_counts = {item["day"]: item["count"] for item in base_qs}
        weekdays = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]
        data = []
        for idx in range(7):
            day = start_date + timedelta(days=idx)
            data.append(
                {
                    "date": day.isoformat(),
                    "weekday": weekdays[day.weekday()],
                    "completed_lessons": day_counts.get(day, 0),
                }
            )
        return data

    def get_recent_activity(self, obj):
        entries = []

        logs = ActivityLog.objects.filter(user=obj).order_by("-timestamp")[:5]
        for log in logs:
            entries.append(
                {
                    "type": "log",
                    "title": log.action,
                    "timestamp": log.timestamp,
                }
            )

        completed_courses = (
            Enrollment.objects.filter(user=obj, is_completed=True)
            .select_related("course")
            .order_by("-enrolled_at")[:3]
        )
        for enrollment in completed_courses:
            entries.append(
                {
                    "type": "course",
                    "title": f"{self._course_title(enrollment.course)} kursini tugatdingiz",
                    "timestamp": enrollment.enrolled_at,
                }
            )

        completed_lessons = (
            CourseProgress.objects.filter(
                user=obj,
                is_complete=True,
                completed__isnull=False,
            )
            .select_related("course")
            .order_by("-completed")[:5]
        )
        for progress in completed_lessons:
            course_title = self._course_title(progress.course)
            entries.append(
                {
                    "type": "lesson",
                    "title": f"{course_title} darsi tugatildi",
                    "timestamp": progress.completed,
                }
            )

        entries.sort(key=lambda item: item["timestamp"], reverse=True)
        return entries[:10]

    def get_achievements(self, obj):
        counts = self._basic_counts(obj)
        streak = self._streak_info(obj)
        achievements = []
        today = timezone.localdate()

        def push(key, title, description, achieved, achieved_at=None, progress=None):
            achievements.append(
                {
                    "key": key,
                    "title": title,
                    "description": description,
                    "achieved": achieved,
                    "achieved_at": achieved_at,
                    "progress": progress,
                }
            )

        first_course = (
            Enrollment.objects.filter(user=obj, is_completed=True)
            .order_by("enrolled_at")
            .first()
        )
        push(
            "first_course",
            "Birinchi qadam",
            "Birinchi kursni tugatdingiz",
            bool(first_course),
            achieved_at=first_course.enrolled_at.date() if first_course else None,
        )

        push(
            "streak_7",
            "7 kunlik streak",
            "7 kun ketma-ket o'qidingiz",
            streak["best"] >= 7,
            achieved_at=today if streak["best"] >= 7 else None,
            progress={"current": streak["current"], "best": streak["best"]},
        )

        lessons_qs = counts["completed_lessons_qs"]
        fiftieth_date = None
        if counts["completed_lessons"] >= 50:
            try:
                fiftieth = lessons_qs.order_by("completed").values_list("completed", flat=True)[49]
                fiftieth_date = fiftieth.date() if fiftieth else None
            except IndexError:
                fiftieth_date = None
        push(
            "50_lessons",
            "50 dars",
            "50 ta darsni tugatdingiz",
            counts["completed_lessons"] >= 50,
            achieved_at=fiftieth_date,
            progress={"completed_lessons": counts["completed_lessons"]},
        )

        month_ago = timezone.now() - timedelta(days=30)
        recent_completed = Enrollment.objects.filter(
            user=obj,
            is_completed=True,
            enrolled_at__gte=month_ago,
        ).count()
        push(
            "speed_learner",
            "Speed Learner",
            "1 oyda 3 ta kurs tugating",
            recent_completed >= 3,
            achieved_at=today if recent_completed >= 3 else None,
            progress={"last_30_days_completed": recent_completed},
        )

        push(
            "master",
            "Master",
            "10 ta kurs tugating",
            counts["completed_courses"] >= 10,
            progress={"completed_courses": counts["completed_courses"]},
        )

        push(
            "streak_30",
            "30 kunlik streak",
            "30 kun ketma-ket o'qish",
            streak["best"] >= 30,
            achieved_at=today if streak["best"] >= 30 else None,
            progress={"current": streak["current"], "best": streak["best"]},
        )

        return achievements

    def get_summary_cards(self, obj):
        counts = self._basic_counts(obj)
        weekly_total = sum(item["completed_lessons"] for item in self.get_weekly_activity(obj))
        streak = self._streak_info(obj)
        current_month_start = timezone.localdate().replace(day=1)
        completed_this_month = Enrollment.objects.filter(
            user=obj, is_completed=True, enrolled_at__date__gte=current_month_start
        ).count()
        return {
            "completed_courses": {
                "value": counts["completed_courses"],
                "delta": f"+{completed_this_month} bu oy",
            },
            "active_courses": {
                "value": counts["active_courses"],
                "note": "Davom etmoqda",
            },
            "completed_lessons": {
                "value": counts["completed_lessons"],
                "delta": f"+{weekly_total} bu hafta",
            },
            "streak": {
                "value": f"{streak['current']} kun",
                "best": streak["best"],
            },
        }

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "phone_number",
            "location",
        ]

    def validate_email(self, value):
        user = self.context["request"].user
        if value and CustomUser.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon mavjud")
        return value
