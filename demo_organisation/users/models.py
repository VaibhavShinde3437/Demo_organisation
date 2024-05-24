from typing import Any
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager, AbstractUser
# Create your models here.

# User = get_user_model()

class CustomUserManager(UserManager):
    def create_superuser(self, username: str, email: str | None, password: str | None, **extra_fields: Any) -> Any:
        return super().create_superuser(username, email, password, **extra_fields)
    

class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    is_admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)
    
    objects = CustomUserManager()
    
    def __str__(self) -> str:
        return self.get_full_name()
    