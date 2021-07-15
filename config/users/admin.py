from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import User, PhoneNumber


class UserAdmin(BaseUserAdmin):
    model = User
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = ('id', 'email', 'username', 'full_name', 'site_points', 'first_language',
                    'datetime_joined', 'last_login', 'is_staff', 'is_active', )
    list_filter = ('email', 'is_staff', 'datetime_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'full_name', 'password', 'first_language', )}),
        ('Permissions', {'fields': ('is_staff', 'is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email', 'full_name', 'site_points', 'first_language', 'is_staff', )
    ordering = ('full_name', 'site_points', 'datetime_joined')


admin.site.register(PhoneNumber)
admin.site.register(User, UserAdmin)
