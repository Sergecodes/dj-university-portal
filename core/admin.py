from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Institution, Country, City


class CountryAdmin(TranslationAdmin):
    pass


class InstitutionAdmin(TranslationAdmin):
    pass


admin.site.register(City)
admin.site.register(Country, CountryAdmin)
admin.site.register(Institution, InstitutionAdmin)
