from django.contrib import admin
from .models import Course, CourseCategory, Question, Section, Video


admin.site.register([Course, CourseCategory, Question, Section, Video])
