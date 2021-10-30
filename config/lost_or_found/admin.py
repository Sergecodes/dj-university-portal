from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import LostItem, FoundItem


class LostItemAdmin(TranslationAdmin):
    pass


class FoundItemAdmin(TranslationAdmin):
    pass


admin.site.register(LostItem, LostItemAdmin)
admin.site.register(FoundItem, FoundItemAdmin)
