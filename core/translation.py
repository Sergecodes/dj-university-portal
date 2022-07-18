from modeltranslation.translator import (
    register, TranslationOptions as TransOptions
)

from .models import Institution, Country


@register(Country)
class CountryTransOptions(TransOptions):
    fields = ('name', )
    # required_languages = ('en', 'fr')  name shouldn't be required in other languages because come school names
    # might not have a translation. ex: SkyHigh ...


@register(Institution)
class InstitutionTransOptions(TransOptions):
    fields = ('name', )
    # required_languages = ('en', 'fr')  name shouldn't be required in other languages because come school names
    # might not have a translation. ex: SkyHigh ...
