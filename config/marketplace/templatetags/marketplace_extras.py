from django import template
from django.template.defaultfilters import stringfilter

from users.utils import parse_phone_number

register = template.Library()

register.filter('parse_tel', parse_phone_number)

@register.filter(name='zip')
def zip_lists(list1, list2):
    return zip(list1, list2)
 

@register.simple_tag
def query_transform(request, **kwargs):
    """Insert kwargs into url"""
    updated = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None:
            updated[k] = v
        else:
            updated.pop(k, 0)

    return updated.urlencode()


# @register.filter
# def parse_tel(value):
#     """
#     Appropriately print a phone number.
#     e.g. 651234566 should return 6 51 23 45 66
#     """
#     result = value[0]
#     n = len(value)
#     for i in range(1, n, 2):
#         temp = value[i] + value[i+1]
#         result = result + ' ' + temp

#     return result