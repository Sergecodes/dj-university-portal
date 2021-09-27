# from modeltranslation.translator import register, TranslationOptions as TransOptions

# from .models import PastPaper


# @register(PastPaper)
# class PastPaperTransOptions(TransOptions):
#     fields = ('title', )
#     required_languages = ('en', 'fr')


### DON'T translate past papers since we would be translating the titles but the paper(files and photos..) will remain in the same language.. so no need to enable translate ..
# Translating the title will also be unneccessary