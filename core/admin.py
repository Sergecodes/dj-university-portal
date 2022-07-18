from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Institution, Country


class CountryAdmin(TranslationAdmin):
    pass


class InstitutionAdmin(TranslationAdmin):
    pass


admin.site.register(Country, CountryAdmin)
admin.site.register(Institution, InstitutionAdmin)
