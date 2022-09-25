from django.apps import AppConfig
from django.db.models.signals import post_save


class QaSiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qa_site'

    def ready(self):
        pass
        # import qa_site.signals
        # from qa_site.models import AcademicComment, DiscussComment

        # post_save.connect(qa_site.signals.set_users_mentioned, AcademicComment)
        # post_save.connect(qa_site.signals.set_users_mentioned, DiscussComment)

