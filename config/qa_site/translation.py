from modeltranslation.translator import register, TranslationOptions as TransOptions

from .models import (
	Subject, AcademicAnswer, SchoolAnswer,
	AcademicAnswerComment, SchoolAnswerComment,
	AcademicQuestion, SchoolQuestion, AcademicQuestionTag,
	AcademicQuestionComment, SchoolQuestionComment
)


@register(AcademicQuestionTag)
class AcademicQuestionTagTransOptions(TransOptions):
	fields = ('name', 'slug')
	# required_languages = ('en', 'fr')


@register(AcademicQuestion)
class AcademicQuestionTransOptions(TransOptions):
	fields = ('title', 'slug', 'content')
	# `content` is optional(can be blank..) so translation should also be optional
	required_languages = {
		'default': ('title', 'slug')
	}
	# check out the empty_values, may be it can be used with google translation...


@register(SchoolQuestion)
class SchoolQuestionTransOptions(TransOptions):
	fields = ('content', )
	# required_languages = ('en', 'fr') 


@register(AcademicAnswer)
class AcademicAnswerTransOptions(TransOptions):
	fields = ('content', )
	required_languages = ('en', 'fr')


@register(SchoolAnswer)
class SchoolAnswerTransOptions(TransOptions):
	fields = ('content', )
	required_languages = ('en', 'fr')


@register(AcademicAnswerComment)
class AcademicAnswerCommentTransOptions(TransOptions):
	fields = ('content', )
	required_languages = ('en', 'fr')


@register(SchoolAnswerComment)
class SchoolAnswerCommentTransOptions(TransOptions):
	fields = ('content', )
	required_languages = ('en', 'fr')  


@register(AcademicQuestionComment)
class AcademicQuestionCommentTransOptions(TransOptions):
	fields = ('content', )
	required_languages = ('en', 'fr')


@register(SchoolQuestionComment)
class SchoolQuestionCommentTransOptions(TransOptions):
	fields = ('content', )
	required_languages = ('en', 'fr') 


@register(Subject)
class SubjectTransOptions(TransOptions):
	fields = ('name', 'slug', )
	required_languages = ('en', 'fr') 