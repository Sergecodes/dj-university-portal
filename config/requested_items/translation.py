from modeltranslation.translator import register, TranslationOptions as TransOptions

from .models import RequestedItem


@register(RequestedItem)
class RequestedItemTransOptions(TransOptions):
    # add `price_at_hand` since it's a char field 
    # and some users might want to add some worded details..
	fields = ('item_requested', 'item_description', 'slug', 'price_at_hand', )
	# required_languages = ('en', 'fr')

