from modeltranslation.translator import register, TranslationOptions as TransOptions

from .models import LostItem, FoundItem


@register(FoundItem)
class FoundItemTransOptions(TransOptions):
	fields = ('item_found', 'slug', 'area_found', 'how_found', )
	# required_languages = ('en', 'fr')


@register(LostItem)
class LostItemTransOptions(TransOptions):
	fields = ('item_lost', 'slug', 'area_lost', 'how_lost', 'bounty', 'item_description')
	# required_languages = ('en', 'fr')
