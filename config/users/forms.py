from django.contrib.auth.forms import (
	UserCreationForm as BaseUserCreationForm,
	UserChangeForm as BaseUserChangeForm
)
from .models import User


class UserCreationForm(BaseUserCreationForm):
	class Meta:
		models 	= User
		fields 	= '__all__'


class UserChangeForm(BaseUserChangeForm):
	class Meta:
		model 	= User
		fields 	= '__all__'
