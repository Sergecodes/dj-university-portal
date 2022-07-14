from django.apps import AppConfig
from django.db.models.signals import post_save



class QaSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qa_site'

    def ready(self):
        import qa_site.signals
        from qa_site.models import AcademicQuestionComment

        post_save.connect(qa_site.signals.comment_posted, sender=AcademicQuestionComment)
