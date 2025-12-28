from django.contrib import admin
from .models import Course, CourseCategory, Test, Question, Section, Video


admin.site.register([Course, CourseCategory, Test, Question, Section, Video])

