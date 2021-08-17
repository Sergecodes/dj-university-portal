from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import PastPaper


class PastPaperAdmin(TranslationAdmin):
    pass

admin.site.register(PastPaper, PastPaperAdmin)
