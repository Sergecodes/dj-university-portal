from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    Subject, AcademicAnswer, 
    AcademicAnswerComment, AcademicQuestionTag,
    AcademicQuestion, DiscussQuestion, 
    AcademicQuestionComment, DiscussComment
)


class AcademicAnswerAdmin(TranslationAdmin):
    pass


class AcademicAnswerCommentAdmin(TranslationAdmin):
    pass


class AcademicQuestionCommentAdmin(TranslationAdmin):
    pass


class DiscussCommentAdmin(TranslationAdmin):
    pass


class QuestionAdmin(TranslationAdmin):
    pass


class DiscussQuestionAdmin(TranslationAdmin):
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
admin.site.register(DiscussQuestion, DiscussQuestionAdmin)
admin.site.register(AcademicQuestionTag, AcademicQuestionTagAdmin)
admin.site.register(AcademicQuestion, AcademicQuestionAdmin)
admin.site.register(AcademicAnswer, AcademicAnswerAdmin)
admin.site.register(AcademicAnswerComment, AcademicAnswerCommentAdmin)
admin.site.register(AcademicQuestionComment, AcademicQuestionCommentAdmin)
admin.site.register(DiscussComment, DiscussCommentAdmin)
