from django.db import models
from django.utils.translation import gettext_lazy as _
from notifications.base.models import AbstractNotification


## Override the django-notifications-hq Notification model
class Notification(AbstractNotification):
    GENERAL = 'G'
    MENTIONS = 'M'
    ACTIVITIES = 'A'

    CATEGORIES = (
        (GENERAL, _('General')),
        (MENTIONS, _('Mentions')),
        (ACTIVITIES, _('Activities'))
    )

    category = models.CharField(choices=CATEGORIES, default='G', max_length=2)


    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'core'




