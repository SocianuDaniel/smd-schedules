from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from django_countries import Countries
from localflavor.it import it_region, it_province
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MaxValueValidator, MinValueValidator


class LimitCountries(Countries):

    only = [
        "IT",
    ]


class UserManager(BaseUserManager):
    """Manager for users"""

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
    company_name = models.CharField(
        verbose_name=_('company name'),
        max_length=250, blank=True
    )
    first_name = models.CharField(
        _('First Name'), max_length=200, blank=True)
    last_name = models.CharField(
        _('Last Name'),
        max_length=200,
        blank=True
    )
    street_name = models.CharField(
        verbose_name=_("street name"),
        max_length=250, blank=True
    )
    street_number = models.CharField(
        verbose_name=_("street number"),
        max_length=20,
        blank=True
    )
    city = models.CharField(
        verbose_name=_("city name"),
        max_length=200,
        blank=True
    )
    zip_code = models.CharField(
        verbose_name=_("zip code"),
        max_length=20,
        blank=True
    )
    province_name = models.CharField(
        verbose_name=_("province name"),
        max_length=250,
        blank=True,
        choices=it_province.PROVINCE_CHOICES)
    region_name = models.CharField(
        verbose_name=_("region name"),
        max_length=250,
        blank=True,
        choices=it_region.REGION_CHOICES
    )
    country_name = CountryField(countries=LimitCountries, default='IT')
    social_security_number = models.CharField(
        verbose_name=_("social security number"),
        max_length=20,
        blank=True
    )
    vat_number = models.CharField(
        verbose_name=_('vat number'),
        max_length=20,
        blank=True
    )
    legal_mail = models.EmailField(blank=True)
    billing_code = models.CharField(
        verbose_name=_("billing code"),
        max_length=10,
        blank=True
    )
    mobile_phone = PhoneNumberField(
        verbose_name=_('mobile'),
        region='IT',
        blank=True
    )
    phone = PhoneNumberField(
        verbose_name=_(' phone'),
        region='IT',
        blank=True
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(_('creation on'), auto_now_add=True)
    updated = models.DateTimeField(_('last updated on'), auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Owner(models.Model):
    """class for owner model"""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.user.__str__()


class Contract(models.Model):
    """class for defining week hours contract"""
    owner = models.ForeignKey(
        Owner,
        related_name='owner_contracts',
        on_delete=models.CASCADE
    )
    weekHours = models.PositiveSmallIntegerField(
        _('week hours'),
        validators=[MinValueValidator(1), MaxValueValidator(40)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'weekHours'],
                name=_('week_hours_unique_by_owner')
            )

        ]

    def __str__(self):
        name = ''
        if len(self.owner.user.company_name):
            name = self.owner.user.company_name
        elif len(self.owner.user.first_name+''+self.owner.user.last_name):
            name = self.owner.user.last_name+' '+self.owner.user.first_name
        else:
            name = self.owner.user.email
        return f'{name}-{self.weekHours}-{_("week hours contract")}'
