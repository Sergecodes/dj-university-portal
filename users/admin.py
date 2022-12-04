from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

from .forms import AdminUserCreationForm, AdminUserChangeForm
from .models import User, PhoneNumber

# class PhoneNumberInline(GenericTabularInline):
#     model = PhoneNumber
#     extra = 1

class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1


class UserAdmin(BaseUserAdmin):
    model = User
    inlines = [PhoneNumberInline, ]

    # The forms to add and change user instances
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'id', 'email', 'username', 'site_points', 'first_language', 'gender', 
        'datetime_joined', 'last_login', 'is_staff', 'is_active', 
    )
    list_filter = ('email', 'gender', 'is_staff', 'datetime_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'first_language', 'gender', 'country' )}),
        ('Permissions', {'fields': ('is_staff', 'is_active',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ('Personal information', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'gender', 'country', )
            }
        ),
        ('Site information', {
            'classes': ('wide', ),
            'fields': ('first_language', 'is_staff', 'is_active' )
            }
        ),
    )
    search_fields = ('email', 'site_points', 'first_language', 'gender', 'is_staff', )
    ordering = ('site_points', 'datetime_joined', )


admin.site.register(PhoneNumber)
admin.site.register(User, UserAdmin)
