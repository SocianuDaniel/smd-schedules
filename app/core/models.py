from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Mamager for users"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must provide an email ....')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """create superusers """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the System"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'


# class Employee(models.Model):
#     """Class for the employee"""
#     owner = models.ForeignKey(
#         get_user_model(),
#         related_name="owner",
#         on_delete=models.CASCADE
#     )
#     firstname = models.CharField(_('First Name'), max_length=250, blank=False)
#     lastname = models.CharField(_('Last Name'), max_length=250, blank=False)
#     email = models.EmailField(_('employee email'))
