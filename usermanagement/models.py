from django.db import models
# user_management/models.py
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone

from usermanagement.functions import CustomValidator
# Create your models here.
class User(AbstractBaseUser):
    username=models.CharField(max_length=200,null=False,unique=True, validators=[CustomValidator.validate_username])
    password=models.CharField(max_length=200,null=False,unique=True,validators=[CustomValidator.validate_password])
    email = models.EmailField(unique=True,validators=[CustomValidator.validate_email])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
    class Meta:
        db_table = 'user'
