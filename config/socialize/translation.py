from modeltranslation.translator import register, TranslationOptions as TransOptions

from .models import SocialProfile


@register(SocialProfile)
class SocialProfileTransOptions(TransOptions):
    fields = ('about_me', 'interests', 'hobbies')
    required_languages = ('en', 'fr')
