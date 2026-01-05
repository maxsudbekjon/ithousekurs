from rest_framework import serializers
from .models import CourseCategory, Course, Video, Section, VideoComment, \
    Question, Test, Answer, ContactUsMessage
from django.contrib.auth import get_user_model
from course_progress.models import CourseRating, CourseProgress
from django.db.models import Avg
from decimal import Decimal

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class CourseCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'description', 'name_uz', 'name_en', 'name_ru', 'description_uz', 'description_en',
                  'description_ru']

    def get_name(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        print(lang)
        if lang == 'ru':
            return obj.name_ru
        elif lang == 'en':
            return obj.name_en
        return obj.name_uz

    def get_description(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.description_ru
        elif lang == 'en':
            return obj.description_en
        return obj.description_uz


class CourseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()
    finish = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    instructor = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'users', 'rating', 'lessons', 'finish', 'category', 'name',
                  'name_uz', 'name_en', 'name_ru', 'description', 'description_uz',
                  'description_en', 'description_ru', 'price', 'duration', 'discount', 'instructor', 'status',
                  'videos',"banner"]

    def get_users(self, obj):
        return CourseProgress.objects.filter(course=obj).count()

    def get_rating(self, obj):
        avg_rating = CourseRating.objects.filter(course=obj).aggregate(Avg('rating'))["rating__avg"]
        return round(avg_rating or Decimal("0.0"), 1)

    def get_lessons(self, obj):
        return Video.objects.filter(section__course=obj).count()

    def get_finish(self, obj):
        part = CourseProgress.objects.filter(course=obj, is_complete=True).count()
        total = CourseProgress.objects.filter(course=obj).count()
        if total == 0:
            return 0
        return round((part / total) * 100, 1)

    def get_name(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        print(lang)
        if lang == 'ru':
            return obj.name_ru
        elif lang == 'en':
            return obj.name_en
        return obj.name_uz

    def get_description(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.description_ru
        elif lang == 'en':
            return obj.description_en
        return obj.description_uz
    
    def get_instructor(self, obj):
        instructor = obj.instructor
        return {
            "full_name": instructor.full_name,
        }

    def get_videos(self, obj):
        videos = Video.objects.filter(section__course=obj)
        return VideoSerializer(videos, many=True, context=self.context).data


class VideoSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ["id", 'section', 'title', 'title_uz', 'title_en', 'title_ru', "video_file", 'duration']

    def get_title(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.title_ru
        elif lang == 'en':
            return obj.title_en
        return obj.title_uz


class SectionSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True
    )

    class Meta:
        model = Section
        fields = ['id', 'title', 'title_uz', 'title_en', 'title_ru', 'duration', 'course', 'course_id']

    def get_title(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.title_ru
        elif lang == 'en':
            return obj.title_en
        return obj.title_uz


class VideoCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoComment
        fields = ['id', 'user', 'text', 'video', 'parent_comment', 'likes']
        read_only_fields = ['likes', 'video', 'user']


class TestSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = '__all__'

    def get_title(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.title_ru
        elif lang == 'en':
            return obj.title_en
        return obj.title_uz

    def get_description(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.description_ru
        elif lang == 'en':
            return obj.description_en
        return obj.description_uz


class QuestionSerializer(serializers.ModelSerializer):
    questtion_text = serializers.SerializerMethodField()
    test = TestSerializer(read_only=True)

    class Meta:
        model = Question
        fields = '__all__'

    def get_questtion_text(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.question_text_ru
        elif lang == 'en':
            return obj.question_text_en
        return obj.question_text_uz


class AnswerSerializer(serializers.ModelSerializer):
    answer_text = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = "__all__"

    def get_answer_text(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.answer_text_ru
        elif lang == 'en':
            return obj.answer_text_en
        return obj.answer_text_uz
    

class ContactUsMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUsMessage
        fields = '__all__'
