from modeltranslation.translator import (
    register, TranslationOptions as TransOptions
)

from .models import (
    AdCategory, ItemSubCategory, ItemCategory,
    ItemListing, AdListing
)


@register(AdCategory)
class AdCategoryTransOptions(TransOptions):
    fields = ('name', )
    required_languages = ('en', 'fr')


@register(ItemSubCategory)
class ItemSubCategoryTransOptions(TransOptions): 
    fields = ('name', )
    required_languages = ('en', 'fr')


@register(ItemCategory)
class ItemCategoryTransOptions(TransOptions):
    fields = ('name', )
    required_languages = ('en', 'fr')


@register(AdListing)
class AdListingTransOptions(TransOptions):
    fields = ('title', 'slug', 'description', 'pricing', )
    # required_languages = ('en', 'fr')  # for english and french, all fields are required
    # just blank=False is applied. We have to apply null=True in model.full_clean() method as per modeltranslation docs
    # Remember Django says no need to use null=True on charfield nd textfield


@register(ItemListing)
class ItemListingTransOptions(TransOptions):
    fields = ('title', 'slug', 'description', 'condition_description')
    # required_languages = ('en', 'fr')

