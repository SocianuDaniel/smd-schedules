
"""
Django admin costumisation
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    ordering = ['id']
    list_display = ['email', 'completion_percentage']
    fieldsets = (
        (None, {"fields": ('email', 'password')}),

        (
            _('Contact Info'),
            {
                'fields': (
                    'company_name',
                    'first_name',
                    'last_name',
                    'street_name',
                    'street_number',
                    'city',
                    'zip_code',
                    'province_name',
                    'region_name',
                    'country_name',
                    'social_security_number',
                    'vat_number',
                    'legal_mail',
                    'billing_code',
                    'mobile_phone',
                    'phone'
                )
            }

        ),


        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }

        ),
        (_('Important Dates'), {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login', 'created']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Owner)
admin.site.register(models.Contract)
admin.site.register(models.Task)
admin.site.register(models.Employee)
admin.site.register(models.Shift)
admin.site.register(models.Schedule)
