from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    AGENT = 'agent'
    COACH = 'coach'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (AGENT, 'Agent'),
        (COACH, 'Coach'),
        (ADMIN, 'Admin'),  # Adding admin as a role
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=COACH)
    email = models.EmailField(unique=True)

    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=100)

    REGISTERED_VIA_CHOICES = [
        ('admin', 'Admin Dashboard'),
        ('coach', 'Coach API'),
        ('agent', 'Agent API'),
        ('other', 'Other'),
    ]
    
    registered_from = models.CharField(max_length=10, choices=REGISTERED_VIA_CHOICES, default='other')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email

    def clean(self):
        if self.role == self.ADMIN and not self.is_superuser:
            raise ValidationError(_('Admin role can only be assigned to superusers.'))
        if self.is_superuser and self.role != self.ADMIN:
            raise ValidationError(_('Superusers must have the admin role.'))

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_agent(self):
        return self.role == self.AGENT

    @property
    def is_coach(self):
        return self.role == self.COACH