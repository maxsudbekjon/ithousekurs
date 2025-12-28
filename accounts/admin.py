from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import CustomUser, Role, Notification, ActivityLog, Teacher
# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )

    list_display = ('phone_number', 'email', 'is_staff', 'role')
    list_filter = ('is_staff', 'role')
    search_fields = ('phone_number', 'email')
    ordering = ('role',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('phone_number', 'email', 'role', 'specialization', 'bio', 'students', 'experience'),
        }),
        ('Personal info', {'fields': ('first_name', 'last_name', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'email', 'role', 'specialization', 'bio', 'students', 'experience'),
        }),
    )

    list_display = ('id', 'full_name', 'specialization')
    list_filter = ('specialization',)
    search_fields = ('user__phone_number', 'user__email')
    # ordering = ('user__username',)

admin.site.register([Role, Notification, ActivityLog])
