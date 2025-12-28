from django.contrib import admin
from .models import Exam, Certificate, CourseProgress, CourseRating

admin.site.register([Exam, Certificate, CourseProgress, CourseRating])
