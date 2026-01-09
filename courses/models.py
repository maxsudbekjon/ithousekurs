from django.db import models
from django.conf import settings


class BasicClass(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CourseCategory(BasicClass):
    name_en = models.CharField(max_length=255)
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    description_en = models.TextField()
    description_uz = models.TextField()
    description_ru = models.TextField()

    def __str__(self):
        return self.name_uz


STATUS_CHOICES = (
    ("boshlangich", "Boshlangich"),
    ("o'rta", "O'rta"),
    ("yuqori", "Yuqori")
)


class Course(BasicClass):
    name_en = models.CharField(max_length=255)
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    description_en = models.TextField()
    description_uz = models.TextField()
    description_ru = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    banner = models.ImageField(upload_to="course_banners/")
    discount = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=15)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    instructor = models.ForeignKey('accounts.Teacher', on_delete=models.CASCADE, related_name='instructor')
    status = models.CharField(max_length=150, choices=STATUS_CHOICES)

    def __str__(self):
        return self.name_uz


class Section(BasicClass):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title_en = models.CharField(max_length=255)
    title_uz = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)
    duration = models.CharField(max_length=15)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"course: {self.course} --> title: {self.title_uz}"


class Video(BasicClass):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    title_en = models.CharField(max_length=255)
    title_uz = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)
    description_en = models.CharField(max_length=255,null=True,blank=True,default="")
    description_uz = models.CharField(max_length=255,null=True,blank=True,default="")
    description_ru = models.CharField(max_length=255,null=True,blank=True,default="")
    video_file = models.FileField(upload_to='videos/')
    duration = models.CharField(max_length=15)
    is_preview = models.BooleanField(default=False)

    def __str__(self):
        return self.title_uz


class VideoComment(BasicClass):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    text = models.TextField()
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField('accounts.CustomUser', related_name='liked_comment', blank=True)

    def __str__(self):
        return self.text


class Question(BasicClass):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    question_text_en = models.TextField()
    question_text_uz = models.TextField()
    question_text_ru = models.TextField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"video: {self.video} --- question_text: {self.question_text_en}"


class Answer(BasicClass):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text_en = models.TextField()
    answer_text_uz = models.TextField()
    answer_text_ru = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'question: {self.question} --- answer: {self.answer_text_uz}'
    

class SectionCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'section')

    def __str__(self):
        return f"{self.user.full_name} completed {self.section.title_uz} at {self.completed_at}"
    

class ContactUsMessage(BasicClass):
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contact_messages')
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.full_name} - {self.phone_number} - {self.course.name_en} - {self.message}"
