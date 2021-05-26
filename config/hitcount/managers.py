from django.db import models
from django.contrib.contenttypes.models import ContentType

class HitCountManager(models.Manager):

    def get_for_object(self, obj):
        """
        To get the related HitCount object for the corresponding model object .
        model_object_hitcount = HitCount.objects.get_for_object(model_object)

        Ofcourse model_object.hfn can also be used; where hfn is the hitcount_field_name of the model object in question.
        But this is more adaptable since it can be used for any object.
        """
        ctype = ContentType.objects.get_for_model(obj)
        hitcount, created = self.get_or_create(content_type=ctype, object_id=obj.pk)

        return hitcount