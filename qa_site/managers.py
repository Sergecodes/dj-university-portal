from django.utils.text import capfirst
from taggit.forms import TagField
from taggit_selectize.managers import TaggableManager as BaseTaggableManager
from .widgets import TagSelectize


class TaggableManager(BaseTaggableManager):
   """Override the widget to our custom widget"""
   def formfield(self, form_class=TagField, **kwargs):
      defaults = {
         "label": capfirst(self.verbose_name),
         "help_text": None,
         "required": not self.blank,
         "widget": TagSelectize,
      }
      
      defaults.update(kwargs)
      return form_class(**defaults)
