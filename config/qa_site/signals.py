# from django.db.models.signals import post_save
# from notifications.signals import notify
# from qa_site.models import MyModel

# def my_handler(sender, instance, created, **kwargs):
# 	notify.send(instance, verb='was saved')

# post_save.connect(my_handler, sender=MyModel)

# notify.send(actor, recipient, verb, action_object, target, level, description, public, timestamp, **kwargs)