from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    AdCategory, ItemSubCategory, ItemListingPhoto, ItemCategory,
    ItemListing, AdListing, AdListingPhoto
)

class ItemListingPhotoInline(admin.TabularInline):
    model = ItemListingPhoto
    extra = 0


class ItemSubCategoryInline(admin.TabularInline):
    model = ItemSubCategory
    extra = 1


class ItemListingAdmin(TranslationAdmin):
    inlines = [ItemListingPhotoInline, ]


class AdListingPhotoInline(admin.TabularInline):
    model = AdListingPhoto
    extra = 0


class AdListingAdmin(TranslationAdmin):
    inlines = [AdListingPhotoInline]


class ItemSubCategoryAdmin(TranslationAdmin):
    pass


class ItemCategoryAdmin(TranslationAdmin):
    inlines = [ItemSubCategoryInline, ]


class AdCategoryAdmin(TranslationAdmin):
    pass


admin.site.register(AdListing, AdListingAdmin)
admin.site.register(ItemListing, ItemListingAdmin)
admin.site.register(ItemSubCategory, ItemSubCategoryAdmin)
admin.site.register(AdCategory, AdCategoryAdmin)
admin.site.register(ItemCategory, ItemCategoryAdmin)
admin.site.register(ItemListingPhoto)
admin.site.register(AdListingPhoto)