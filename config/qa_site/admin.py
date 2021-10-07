from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    Subject, AcademicAnswer, SchoolAnswer,
    AcademicAnswerComment, SchoolAnswerComment,
    AcademicQuestion, SchoolQuestion, AcademicQuestionTag,
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


class AcademicQuestionCommentAdmin(TranslationAdmin):
    pass


class SchoolQuestionCommentAdmin(TranslationAdmin):
    pass


class QuestionAdmin(TranslationAdmin):
    pass


class SchoolQuestionAdmin(TranslationAdmin):
    pass


class AcademicQuestionTagAdmin(TranslationAdmin):
    pass


class AcademicQuestionAdmin(TranslationAdmin):
    list_display = ['tag_list']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return ', '.join([o.name for o in obj.tags.all()])


class SubjectAdmin(TranslationAdmin):
    pass
        

admin.site.register(Subject, SubjectAdmin)
admin.site.register(SchoolQuestion, SchoolQuestionAdmin)
admin.site.register(AcademicQuestionTag, AcademicQuestionTagAdmin)
admin.site.register(AcademicQuestion, AcademicQuestionAdmin)
admin.site.register(AcademicAnswer, AcademicAnswerAdmin)
admin.site.register(SchoolAnswer, SchoolAnswerAdmin)
admin.site.register(AcademicAnswerComment, AcademicAnswerCommentAdmin)
admin.site.register(SchoolAnswerComment, SchoolAnswerCommentAdmin)
admin.site.register(AcademicQuestionComment, AcademicQuestionCommentAdmin)
admin.site.register(SchoolQuestionComment, SchoolQuestionCommentAdmin)
