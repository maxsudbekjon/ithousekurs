from django.db import models
from courses.models import BasicClass, Test, Course, Video
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class CourseRating(BasicClass):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_rating_user')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    feedback = models.TextField()

    def __str__(self):
        return f"course: {self.course} --> rating: {self.rating}"


class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress_user')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video_progress = models.ForeignKey(Video, on_delete=models.CASCADE)
    test_progress = models.ForeignKey(Test, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    completed = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.is_complete and not self.completed:
            self.completed = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"user: {self.user} -- course: {self.course}"


class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title_en = models.CharField(max_length=255)
    title_uz = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)
    duration = models.CharField(max_length=15)
    start_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title_en


RESULT_CHOICE = (
    ('passed', 'Passed'),
    ('failed', 'Failed')
)


class ExamResult(BasicClass):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_result_user')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    score = models.CharField(max_length=120)
    result = models.CharField(max_length=150, choices=RESULT_CHOICE)

    def __str__(self):
        return f"exam: {self.exam} --> result: {self.result}"
    

class TestResult(BasicClass):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_result_user')
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=10, decimal_places=2)
    is_passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user} --> test: {self.test} --> score: {self.score}"

class Certificate(BasicClass):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificate_user')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(upload_to='certificates/', blank=True)
    certificate_id = models.CharField(max_length=155)

    def __str__(self):
        return self.certificate_id
