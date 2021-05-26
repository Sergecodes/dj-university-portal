from modeltranslation.translator import register, TranslationOptions as TransOptions
from .models import Category, ParentCategory, Ad, Item, Institution


@register(Category)
class CategoryTransOptions(TransOptions):  # "TO" stands for Translation Options
    fields = ('name', )
    required_languages = ('en', 'fr')


@register(ParentCategory)
class ParentCategoryTransOptions(TransOptions):
    fields = ('name', )
    required_languages = ('en', 'fr')


class PostTransOptions(TransOptions):
    fields = ('title', 'slug', 'description')
    required_languages = ('en', 'fr')  # for english and french, all fields are required
    # just blank=False is applied. We have to apply null=True in model.full_clean() method as per modeltranslation docs
    # Remember Django says no need to use null=True on charfield nd textfield


@register(Ad)
class AdTransOptions(PostTransOptions):
    pass


@register(Item)
class ItemTransOptions(PostTransOptions):
    fields = ('condition_description', )


@register(Institution)
class InstitutionTransOptions(TransOptions):
    fields = ('name', )
    # required_languages = ('en', 'fr')  name shouldn't be required in other languages because come school names
    # might not have a translation. ex: SkyHigh ...

