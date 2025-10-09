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
from django.core.exceptions import ValidationError
from django .db.models import Q


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


class Employee(models.Model):
    """class for employee mode"""
    owner = models.ForeignKey(
        Owner,
        related_name='employee_owner',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    contract = models.ForeignKey(
        Contract,
        related_name='employee_contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    startDate = models.DateField(_('activity start date'))
    endDate = models.DateField(_('activity end date'), null=True, blank=True)

    def __str__(self):

        name = ''
        if len(self.user.company_name):
            name = self.user.company_name
        elif len(self.user.first_name + '' + self.user.last_name):
            name = self.user.last_name + ' ' + self.user.first_name
        else:
            name = self.user.email
        return name


class Task(models.Model):
    """class for shift  task"""
    owner = models.ForeignKey(
        Owner,
        related_name='owner_tasks',
        on_delete=models.CASCADE

    )
    name = models.CharField(_('task name'), max_length=250, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'],
                name=_('unique_task_by_owner')
            )

        ]

    def __str__(self):
        return self.name


class Shift(models.Model):
    """models for shift """
    owner = models.ForeignKey(
        Owner,
        related_name='owner_shift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    employee = models.ForeignKey(
        Employee,
        related_name='employee_shift',
        on_delete=models.CASCADE
    )
    shift_date = models.DateField(
        _('shift_date')
    )
    start_time = models.DateTimeField(
        _('shift_start_time')
    )
    end_time = models.DateTimeField(
        _('shift end time')
    )
    task = models.ForeignKey(
        Task,
        related_name='shift_task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f'' \
               f'[{self.employee}]-' \
               f'{self.shift_date}' \
               f'[{self.start_time: %H:%M}-{self.end_time: %H:%M}]' \
               f'-[{self.task}]'

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(
                _('the shift must end after the start time')
            )
        overlapping_shifts = Shift.objects.filter(
            employee=self.employee,
            shift_date=self.shift_date,
        ).filter(
            Q(start_time__lt=self.end_time) & Q(end_time__gt=self.start_time)
        )
        if self.pk:
            overlapping_shifts = overlapping_shifts.exclude(pk=self.pk)
        if overlapping_shifts.exists():
            raise ValidationError(
                _(f'Shift conflict with {overlapping_shifts}')
            )
        super().clean()
