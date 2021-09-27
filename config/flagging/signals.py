from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from notifications.signals import notify

from core.constants import SHOULD_FLAG_COUNT
from .models import Flag, FlagInstance


@receiver(post_save, sender=FlagInstance)
def flagged(sender, instance, created, raw, using, update_fields, **kwargs):
    """Increase flag count in the flag model after creating an instance"""
    if created:    
        flag = instance.flag
        flag.increase_count()
        flag.toggle_flagged_state()

        # NOTE that post is considered FLAGGED when count (SHOULD_FLAG_COUNT) FLAGS_ALLOWED + 1
        # for each flagged post, `IF` post's flag count is = SHOULD_FLAG_COUNT (if post should be FLAGGED)
        # (this is a newly flagged post), penalize poster (deduct points.)
        # `ELSE` if post's flag count is a multiple of (SHOULD_FLAG_COUNT) 
        # i.e. perhaps if moderators haven't yet reviewed the post
        # delete the post (without penalizing poster again)

        # enter this condition only when necessary (only when count is a multiple of SHOULD_FLAG_COUNT)
        if (count := flag.count) % SHOULD_FLAG_COUNT == 0:
            object = flag.content_object
            # all flaggable objects must have a `poster` property.
            poster = object.poster

            # if post is newly FLAGGED
            if count == SHOULD_FLAG_COUNT:
                poster.penalize_flagged_user(flagged_post=object)

            # if post has already been FLAGGED and is still FLAGGED (let's say "doubly FLAGGED") but moderator hasn't yet reviewed or deleted
            # auto delete
            if count == (2 * SHOULD_FLAG_COUNT):
                object.delete()
                # TODO Notify poster
                notify.send(
                    sender=poster,  # just use poster as sender
                    recipient=poster, 
                    verb=_("One of your posts has been deleted because it was flagged multiple times and was considered innapropriate by many users. Ensure to avoid posting such posts in future."),
                )


@receiver(post_delete, sender=FlagInstance)
def unflagged(sender, instance, using, **kwargs):
    """Decrease flag count in the flag model before deleting an instance"""
    flag = instance.flag
    flag.decrease_count()
    flag.toggle_flagged_state()


# the following signals are registered in flagging.__init__'s ready method.

def create_permission_groups(sender, **kwargs):
    """Create permissions related to flagging."""
    flag_ct = ContentType.objects.get_for_model(Flag)
    delete_flagged_perm, __ = Permission.objects.get_or_create(
        codename='delete_flagged_content',
        name=_('Can delete flagged content'),
        content_type=flag_ct
    )
    moderator_group, __ = Group.objects.get_or_create(name='flag_moderator')
    moderator_group.permissions.add(delete_flagged_perm)


def adjust_flagged_content(sender, **kwargs):
    """Adjust flag state perhaps after changing FLAGS_ALLOWED count"""
    for flag in Flag.objects.all():
        flag.toggle_flagged_state()
