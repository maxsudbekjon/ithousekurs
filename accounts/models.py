from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from uuid import uuid4
from accounts.manager import CustomUserManager


class Role(models.Model):
    name_eng = models.CharField(max_length=50, unique=True)
    name_uz = models.CharField(max_length=50, unique=True)
    name_ru = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name_eng


class CustomUser(AbstractUser):
    id = models.UUIDField(
        unique=True,
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True,
                                        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    rating = models.PositiveIntegerField(default=0)
    password = models.CharField(max_length=128, null=True, blank=True)
    finished_courses = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users', null=True, blank=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'
        ordering = ['-created_at']
        unique_together = ('email', 'phone_number')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    def check_email(self):
        if self.email:
            normalize_email = self.email.lower().strip()
            self.email = normalize_email

    def chaged_hash_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
            self.save()

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name
    

class Teacher(CustomUser):
    specialization = models.CharField(max_length=100)
    bio = models.TextField(null=True, blank=True)
    students = models.PositiveIntegerField(default=0)
    experience = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'teachers'
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

    def __str__(self):
        return f"{self.full_name} - {self.specialization}"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('news', 'News'),
        ('payment', 'Payment'),
        ('enrollment', 'Enrollment'),
        ('course_update', 'Course Update'),
        ('certificate', 'Certificate'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title_en = models.CharField(max_length=50)
    title_uz = models.CharField(max_length=50)
    title_ru = models.CharField(max_length=50)
    message_en = models.TextField()
    message_uz = models.TextField()
    message_ru = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='news')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.full_name}: {self.message[:20]}..."


class ActivityLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=125)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.full_name} - {self.action} at {self.timestamp}"
    

class Enrollment(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.full_name} enrolled in {self.course.name}"
