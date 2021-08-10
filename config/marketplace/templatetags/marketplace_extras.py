from django import template
from django.template.defaultfilters import stringfilter

from users.utils import parse_phone_number

register = template.Library()

register.filter('parse_tel', parse_phone_number)

@register.filter(name='zip')
def zip_lists(list1, list2):
    return zip(list1, list2)
 

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