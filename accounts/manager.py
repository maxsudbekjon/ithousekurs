from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        if not email and not extra_fields.get("phone_number") and not extra_fields.get("is_superuser"):
            raise ValueError("Email yoki telefon raqam mavjud bolishi kerak")

        email = self.normalize_email(email) if email else None
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        from accounts.models import Role
        superuser_role, _ = Role.objects.get_or_create(name_eng='Superuser')
        extra_fields.setdefault('role', superuser_role)

        return self.create_user(phone_number, email, password, **extra_fields)