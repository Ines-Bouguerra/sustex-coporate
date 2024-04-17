from django.db import models
# user_management/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
# Create your models here.
class CustomUser(AbstractBaseUser):
    username=models.CharField(max_length=200,null=False,unique=True)
    password=models.CharField(max_length=200,null=False,unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email