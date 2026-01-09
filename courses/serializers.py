from rest_framework import serializers
from .models import CourseCategory, Course, Video, Section, VideoComment, \
    Question, Answer, ContactUsMessage
from django.contrib.auth import get_user_model
from course_progress.models import CourseRating, CourseProgress
from courses.utils import build_video_access_map
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
    category_name = serializers.SerializerMethodField()

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
        fields = ['id', 'users', 'rating', 'lessons', 'finish', 'category_name', 'name',
                  'name_uz', 'name_en', 'name_ru','description', 'description_uz',
                  'description_en', 'description_ru', 'price', 'duration', 'discount', 'instructor', 'status',
                  'videos',"banner"]
    def get_category_name(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        category = obj.category

        if lang == 'ru':
            return category.name_ru
        elif lang == 'en':
            return category.name_en
        return category.name_uz
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
            "id":instructor.id,
            "full_name": instructor.full_name,
        }

    def get_videos(self, obj):
        videos = Video.objects.filter(section__course=obj,is_preview=True)
        request = self.context.get('request')
        access_map = build_video_access_map(request.user, obj) if request else None
        return VideoSerializer(
            videos,
            many=True,
            context={'request': request, 'access_map': access_map}
        ).data


class VideoSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()
    has_questions = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ["id", 'section', 'title', 'title_uz', 'title_en', 'title_ru', 'description_uz', 'description_en', 'description_ru', "video_file", 'duration',
                  'is_preview', 'is_locked', 'has_questions']

    def get_title(self, obj):
        lang = self.context['request'].LANGUAGE_CODE
        if lang == 'ru':
            return obj.title_ru
        elif lang == 'en':
            return obj.title_en
        return obj.title_uz

    def get_is_locked(self, obj):
        access_map = self.context.get("access_map")
        if access_map is None:
            return False
        return not access_map.get(obj.id, False)

    def get_has_questions(self, obj):
        return Question.objects.filter(video=obj).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("video_file", None)
        return data


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
    
class QuestionSerializer(serializers.ModelSerializer):
    questtion_text = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()

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
    def get_answers(self, obj):
        answers = obj.answer_set.all()
        serializer = AnswerSerializer(
            answers,
            many=True,
            context=self.context
        )
        return serializer.data



    

class ContactUsMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUsMessage
        fields = '__all__'
