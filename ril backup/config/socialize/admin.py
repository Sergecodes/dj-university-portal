from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import SocialProfile


class SocialProfileAdmin(TranslationAdmin):
    pass


admin.site.register(SocialProfile, SocialProfileAdmin)
