from modeltranslation.translator import register, TranslationOptions as TransOptions

from .models import SocialProfile


@register(SocialProfile)
class SocialProfileTransOptions(TransOptions):
    fields = ('speciality', 'about_me', 'hobbies')
    # required_languages = ('en', 'fr')
