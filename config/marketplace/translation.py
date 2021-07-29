from modeltranslation.translator import register, TranslationOptions as TransOptions
from .models import ItemCategory, ItemParentCategory, Ad, ItemListing, Institution
from .models import (
    AdCategory, ItemCategory, ItemParentCategory,
    ItemListing, Ad, Institution
)


@register(AdCategory)
class AdCategoryTransOptions(TransOptions):
    fields = ('name', )
    required_languages = ('en', 'fr')


@register(ItemCategory)
class CategoryTransOptions(TransOptions):  # "TO" stands for Translation Options
    fields = ('name', )
    required_languages = ('en', 'fr')


@register(ItemParentCategory)
class ItemParentCategoryTransOptions(TransOptions):
    fields = ('name', )
    required_languages = ('en', 'fr')


@register(Ad)
class AdTransOptions(TransOptions):
    fields = ('title', 'slug', 'description')
    required_languages = ('en', 'fr')  # for english and french, all fields are required
    # just blank=False is applied. We have to apply null=True in model.full_clean() method as per modeltranslation docs
    # Remember Django says no need to use null=True on charfield nd textfield


@register(ItemListing)
class ItemListingTransOptions(TransOptions):
    fields = ('title', 'slug', 'description', 'condition_description')
    required_languages = ('en', 'fr')


@register(Institution)
class InstitutionTransOptions(TransOptions):
    fields = ('name', )
    # required_languages = ('en', 'fr')  name shouldn't be required in other languages because come school names
    # might not have a translation. ex: SkyHigh ...

