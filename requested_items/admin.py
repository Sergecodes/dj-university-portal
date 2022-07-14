from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import RequestedItemPhoto, RequestedItem


class RequestedItemPhotoInline(admin.TabularInline):
	model = RequestedItemPhoto
	extra = 0


class RequestedItemAdmin(TranslationAdmin):
	inlines = [RequestedItemPhotoInline]


admin.site.register(RequestedItem, RequestedItemAdmin)
admin.site.register(RequestedItemPhoto)
