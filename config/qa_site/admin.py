from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    Subject, AcademicAnswer, SchoolAnswer,
    AcademicAnswerComment, SchoolAnswerComment,
    AcademicQuestion, SchoolQuestion, SchoolQuestionTag,
    AcademicQuestionComment, SchoolQuestionComment
)


class AcademicAnswerAdmin(TranslationAdmin):
    pass


class SchoolAnswerAdmin(TranslationAdmin):
    pass


class AcademicAnswerCommentAdmin(TranslationAdmin):
    pass


class SchoolAnswerCommentAdmin(TranslationAdmin):
    pass


class AcademicQuestionAdmin(TranslationAdmin):
    pass


class SchoolQuestionTagAdmin(TranslationAdmin):
    pass


class QuestionAdmin(TranslationAdmin):
    list_display = ['tag_list']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return ', '.join(o.name for o in obj.tags.all())


class SchoolQuestionAdmin(QuestionAdmin):
    pass


class AcademicQuestionCommentAdmin(QuestionAdmin):
    pass


class SchoolQuestionCommentAdmin(TranslationAdmin):
    pass


class SubjectAdmin(TranslationAdmin):
    pass
        

admin.site.register(Subject, SubjectAdmin)
admin.site.register(SchoolQuestionTag, SchoolQuestionTagAdmin)
admin.site.register(SchoolQuestion, SchoolQuestionAdmin)
admin.site.register(AcademicQuestion, AcademicQuestionAdmin)
admin.site.register(AcademicAnswer, AcademicAnswerAdmin)
admin.site.register(SchoolAnswer, SchoolAnswerAdmin)
admin.site.register(AcademicAnswerComment, AcademicAnswerCommentAdmin)
admin.site.register(SchoolAnswerComment, SchoolAnswerCommentAdmin)
admin.site.register(AcademicQuestionComment, AcademicQuestionCommentAdmin)
admin.site.register(SchoolQuestionComment, SchoolQuestionCommentAdmin)
