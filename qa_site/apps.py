from django.apps import AppConfig
from django.db.models.signals import post_save

from qa_site.models import AcademicQuestionComment


class QaSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qa_site'

    def ready(self):
        import qa_site.signals

        post_save.connect(qa_site.signals.comment_posted, sender=AcademicQuestionComment)
