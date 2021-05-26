from datetime import timedelta
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.db import models
from django.db.models import F
from django.dispatch import receiver, Signal
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .managers import HitCountManager

cache = caches['default']
delete_hit = Signal(providing_args=['save_hitcount'])


@receiver(delete_hit)
def delete_hit_handler(sender, instance, save_hitcount=False, **kwargs):
    """
    Custom callback for the Hit.delete() method.

    Hit.delete(): removes the hit from the associated HitCount object.
    Hit.delete(save_hitcount=True): preserves the hit for the associated
    HitCount object.
    """
    if not save_hitcount:
        instance.hitcount.decrease()


class HitCount(models.Model):
    num_of_hits = models.PositiveIntegerField(default=0)
    modified = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = HitCountManager()

    def __str__(self):
        # return '%s' % self.content_object.id   # db query to get content_object!
        return '%s' % self.object_id

    class Meta:
        # ordering = ('-num_of_hits',)
        get_latest_by = "modified"  # see https://docs.djangoproject.com/en/dev/ref/models/querysets/#latest
        unique_together = ("content_type", "object_id")
        verbose_name = _("hit count")
        verbose_name_plural = _("hit counts")

    def increase(self):
        num_of_hits = cache.get(f'hitcount_{self.id}_hits')
        if num_of_hits:
            self.num_of_hits = num_of_hits + 1
        else:
            self.num_of_hits = F('num_of_hits') + 1
        cache.set(f'hitcount_{self.id}_hits', self.num_of_hits)
        self.save(update_fields=['num_of_hits', 'modified'])

    def decrease(self):
        num_of_hits = cache.get(f'hitcount_{self.id}_hits')
        if num_of_hits:
            self.num_of_hits = num_of_hits - 1
        else:
            self.num_of_hits = F('num_of_hits') - 1
        cache.set(f'hitcount_{self.id}_hits', self.num_of_hits)
        self.save(update_fields=['num_of_hits', 'modified'])

    def hits_in_last(self, **kwargs):
        """
        Returns hit count for an object during a given time period.

        This will only work for as long as hits are saved in the Hit database.
        If you are purging your database after 45 days, for example, that means
        that asking for hits in the last 60 days will return an incorrect
        number as that the longest period it can search will be 45 days.

        For example: hits_in_last(days=7).

        Accepts days, seconds, microseconds, milliseconds, minutes,
        hours, and weeks.  It's creating a datetime.timedelta object.
        """
        assert kwargs, "Must provide at least one timedelta arg (eg, days=1)"

        period = timezone.now() - timedelta(**kwargs)
        return self.hits.filter(created__gte=period).count()


class Hit(models.Model):
    """
    Model captures a single Hit by a visitor.

    None of the fields are editable because they are all dynamically created.
    Browsing the Hit list in the Admin will allow one to blacklist both
    IP addresses as well as User Agents. Blacklisting simply causes those
    hits to not be counted or recorded.

    Depending on how long you set the HITCOUNT_KEEP_HIT_ACTIVE, and how long
    you want to be able to use `HitCount.hits_in_last(days=30)` you can choose
    to clean up your Hit table by using the management `hitcount_cleanup`
    management command.
    """
    created = models.DateTimeField(editable=False, auto_now_add=True)
    ip = models.GenericIPAddressField(unpack_ipv4=True, editable=False, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, editable=False, on_delete=models.CASCADE)
    session = models.CharField(max_length=40, editable=False, db_index=True)
    user_agent = models.CharField(max_length=255, editable=False)
    hitcount = models.ForeignKey(
        HitCount,
        related_name='hits',
        related_query_name='hit',
        editable=False,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('-created',)
        get_latest_by = 'created'
        verbose_name = _("hit")
        verbose_name_plural = _("hits")

    def __str__(self):
        return 'Hit: %s' % self.pk

    def save(self, *args, **kwargs):
        """
        The first time the object is created and saved, we increment
        the associated HitCount object by one. The opposite applies
        if the Hit is deleted.

        """
        if self.pk is None:
            self.hitcount.increase()

        super().save(*args, **kwargs)

    def delete(self, save_hitcount=False):
        """
        If a Hit is deleted and save_hitcount=True, it will preserve the
        HitCount object's total. However, under normal circumstances, a
        delete() will trigger a subtraction from the HitCount object's total.

        NOTE: This doesn't work at all during a queryset.delete(). 
              To workaround this, loop through the queryset and delete individual hits.
        """
        delete_hit.send(
            sender=self, instance=self, save_hitcount=save_hitcount)
        super().delete()


class BlacklistedIP(models.Model):
    ip = models.GenericIPAddressField(unpack_ipv4=True, editable=False, unique=True)

    class Meta:
        verbose_name = _("Blacklisted IP")
        verbose_name_plural = _("Blacklisted IPs")

    def __str__(self):
        return '%s' % self.ip


class BlacklistedUserAgent(models.Model):
    user_agent = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = _("Blacklisted User Agent")
        verbose_name_plural = _("Blacklisted User Agents")

    def __str__(self):
        return '%s' % self.user_agent


class HitCountMixin:
    """
    HitCountMixin provides an easy way to add a `hit_count` property to your
    model that will return the related HitCount object.
    """

    @property
    def hitcount(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        hitcount, created = HitCount.objects.get_or_create(content_type=ctype, object_id=self.pk)

        return hitcount

    # @property
    # def hitcount_pk(self):
    #     return self.hitcount.pk
