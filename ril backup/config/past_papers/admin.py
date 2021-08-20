from django.contrib import admin
# from modeltranslation.admin import TranslationAdmin

from .models import PastPaper


class PastPaperAdmin(admin.ModelAdmin):
    pass


admin.site.register(PastPaper, PastPaperAdmin)
