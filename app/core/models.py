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

    def completion_percentage(self):

        single_fields = [
            'company_name', 'first_name', 'last_name', 'street_name',
            'street_number', 'city', 'zip_code', 'province_name',
            'region_name', 'country_name',
            'social_security_number', 'vat_number', 'billing_code'
        ]

        total = len(single_fields) + 2

        filled = sum(1 for field in single_fields
                     if getattr(self, field) and
                     str(getattr(self, field)).strip()
                     )

        if (self.email and str(self.email).strip()) or \
                (self.legal_mail and str(self.legal_mail).strip()):
            filled += 1

        if (self.mobile_phone and str(self.mobile_phone).strip()) or \
                (self.phone and str(self.phone).strip()):
            filled += 1

        percentage = (filled / total) * 100 if total > 0 else 0
        return round(percentage, 2)

    def get_full_name(self):
        name = f'{self.first_name} {self.last_name}'
        return name if len(name) else self.get_username()

    def get_short_name(self):
        name = ""
        if self.first_name:
            name = f'{self.first_name[0]}.{self.first_name}'
        return name if len(name) else self.get_username()

    def __str__(self):
        return self.company_name \
            if self.company_name else self.get_full_name()


class Owner(models.Model):
    """class for owner model"""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.user.__str__()

    def clean(self):
        if self.user.is_superuser:
            raise ValidationError(
                _('Owner cant be a superuser')
            )

        if Employee.objects.filter(user=self.user).exists():
            raise ValidationError(_("The owner can't be an Employee"))


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
        return f'{self.owner}-{self.weekHours}-{_("week hours contract")}'


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

    def short(self):
        return self.user.get_short_name()

    def __str__(self):
        return self.user.__str__()


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


class Schedule(models.Model):
    owner = models.ForeignKey(
        Owner, related_name='daly_schedule',
        on_delete=models.CASCADE
    )
    date = models.DateField(_('schedule date'))
    start = models.DateTimeField(_('activity datetime start'))
    end = models.DateTimeField(_('activity datetime end'))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'date'],
                name='unique_schedule_by_owner'
            )
        ]

    def __str__(self):
        return f'{self.owner} schedule for {self.date}'

    def clean(self):
        if self.start.date() != self.date:
            raise ValidationError(_('start datetime must greater or equal '))
        if self.end <= self.start:
            raise ValidationError(
                _('end activity must be greater then the start datetime')
            )


class Shift(models.Model):
    """models for shift """
    schedule = models.ForeignKey(
        Schedule,
        related_name='daily_shift',
        on_delete=models.CASCADE,
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
        if self.schedule.owner != self.employee.owner:
            raise ValidationError(
                _('Schedule and Employee mut have the same owner')
            )
        if not (self.schedule.start <= self.start_time <= self.schedule.end):
            raise ValidationError(
                _('shift start date must be within schedule start end')
            )
        if not (self.schedule.start < self.end_time <= self.schedule.end):
            raise ValidationError(
                _('shift start date must be lowerr then schedule end')
            )
        if self.shift_date != self.schedule.date:
            raise ValidationError(_('Shift date must match schedule date'))
        super().clean()
