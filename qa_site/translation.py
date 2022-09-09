from modeltranslation.translator import register, TranslationOptions as TransOptions

from .models import (
	Subject, AcademicComment, DiscussComment,
	AcademicQuestion, DiscussQuestion, QuestionTag,
)


@register(QuestionTag)
class QuestionTagTransOptions(TransOptions):
	fields = ('name', 'slug')
	# required_languages = ('en', 'fr')


@register(AcademicQuestion)
class AcademicQuestionTransOptions(TransOptions):
	fields = ('title', 'slug', 'content')
	# required_languages = {
	# 	'default': ('title', 'slug')
	# }
	# check out the empty_values, may be it can be used with google translation...


@register(DiscussQuestion)
class DiscussQuestionTransOptions(TransOptions):
	fields = ('content', )
	# required_languages = ('en', 'fr') 


@register(AcademicComment)
class AcademicCommentTransOptions(TransOptions):
	fields = ('content', )
	# required_languages = ('en', 'fr')


@register(DiscussComment)
class DiscussCommentTransOptions(TransOptions):
	fields = ('content', )
	# required_languages = ('en', 'fr') 


@register(Subject)
class SubjectTransOptions(TransOptions):
	fields = ('name', 'slug', )
	required_languages = ('en', 'fr') 