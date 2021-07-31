from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    AdCategory, ItemSubCategory, ItemListingPhoto, ItemCategory,
    ItemListing, Ad, Institution, AdPhoto
)


class ItemListingAdmin(TranslationAdmin):
    pass


class AdAdmin(TranslationAdmin):
    pass


class InstitutionAdmin(TranslationAdmin):
    pass


class ItemSubCategoryAdmin(TranslationAdmin):
    pass


class ItemCategoryAdmin(TranslationAdmin):
    pass


class AdCategoryAdmin(TranslationAdmin):
    pass


admin.site.register(Ad, AdAdmin)
admin.site.register(ItemListing, ItemListingAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(ItemSubCategory, ItemSubCategoryAdmin)
admin.site.register(AdCategory, AdCategoryAdmin)
admin.site.register(ItemCategory, ItemCategoryAdmin)
admin.site.register(ItemListingPhoto)
admin.site.register(AdPhoto)