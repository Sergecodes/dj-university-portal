from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    Subject, AcademicComment, DiscussComment,
    QuestionTag, AcademicQuestion, DiscussQuestion, 
)


class AcademicCommentAdmin(TranslationAdmin):
    pass


class DiscussCommentAdmin(TranslationAdmin):
    pass


class QuestionAdmin(TranslationAdmin):
    pass


class DiscussQuestionAdmin(TranslationAdmin):
    pass


class QuestionTagAdmin(TranslationAdmin):
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
admin.site.register(QuestionTag, QuestionTagAdmin)
admin.site.register(AcademicQuestion, AcademicQuestionAdmin)
admin.site.register(AcademicComment, AcademicCommentAdmin)
admin.site.register(DiscussComment, DiscussCommentAdmin)
