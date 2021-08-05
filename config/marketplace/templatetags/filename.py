import os
from django import template

register = template.Library()

@register.filter
def filename(value):
    """Get file name of a file"""
    return os.path.basename(value.file.name)

