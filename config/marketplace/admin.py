from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import (
    Item, Ad,
    Institution, Category,
    ParentCategory
)


class ItemAdmin(TranslationAdmin):
    pass


class AdAdmin(TranslationAdmin):
    pass


class InstitutionAdmin(TranslationAdmin):
    pass


class CategoryAdmin(TranslationAdmin):
    pass


class ParentCategoryAdmin(TranslationAdmin):
    pass


admin.site.register(Ad, AdAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ParentCategory, ParentCategoryAdmin)
