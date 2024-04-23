from django.db import models
# user_management/models.py
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)
from django.db import models
from django.utils import timezone

from usermanagement.functions import CustomValidator

class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given username and password.
        """
        pass

    def create_superuser(self, username, password=None):
        """
        Creates and saves a superuser with the given username and password.
        """
        pass

# Create your models here.
class User(AbstractBaseUser):
    # id = models.AutoField(primary_key=True) 
    username=models.CharField(max_length=200,null=False,unique=True, validators=[CustomValidator.validate_username])
    password=models.CharField(max_length=200,null=False,unique=True,validators=[CustomValidator.validate_password])
    email = models.EmailField(unique=True,validators=[CustomValidator.validate_email])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = MyUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.email
    class Meta:
        db_table = 'user'
