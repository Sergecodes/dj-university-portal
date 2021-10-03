from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Institution


class InstitutionAdmin(TranslationAdmin):
    pass


admin.site.register(Institution, InstitutionAdmin)