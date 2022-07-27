from modeltranslation.translator import register, TranslationOptions as TransOptions

from .models import (
	Subject, AcademicAnswer, AcademicAnswerComment,
	AcademicQuestion, DiscussQuestion, QuestionTag,
	AcademicQuestionComment, DiscussComment
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


@register(AcademicAnswer)
class AcademicAnswerTransOptions(TransOptions):
	fields = ('content', )
	# required_languages = ('en', 'fr')


@register(AcademicAnswerComment)
class AcademicAnswerCommentTransOptions(TransOptions):
	fields = ('content', )
	# required_languages = ('en', 'fr')


@register(AcademicQuestionComment)
class AcademicQuestionCommentTransOptions(TransOptions):
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