from rest_framework import serializers
from .models import QuestionResult, CourseProgress, CourseRating, Exam

class QuestionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionResult
        fields = "__all__"
        read_only_fields = ["user", "is_passed", "completed_at"]


class CourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgress
        fields = "__all__"
        read_only_fields = ["user"]


class CourseRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRating
        fields = '__all__'
        

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'
