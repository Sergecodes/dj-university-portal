import re

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from .models import BlacklistedIP, BlacklistedUserAgent, Hit, HitCount

# this is not intended to be an all-knowing IP address regex
IP_RE = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
HITCOUNT_HITS_PER_IP_LIMIT = 1
EXCLUDE_USER_GROUP = []


def get_ip(request):
    """
    Retrieves the remote IP address from the request data.  If the user is
    behind a proxy, they may have a comma-separated list of IP addresses, so
    we need to account for that.  In such a case, only the first IP in the
    list will be retrieved.  Also, some hosts that use a proxy will put the
    REMOTE_ADDR into HTTP_X_FORWARDED_FOR.  This will handle pulling back the
    IP from the proper place.

    **NOTE** This function was taken from django-tracking (MIT LICENSE)
             http://code.google.com/p/django-tracking/
    """

    # if neither header contain a value, just use local loopback
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR',
                                  request.META.get('REMOTE_ADDR', '127.0.0.1'))
    if ip_address:
        # make sure we have one and only one IP
        try:
            ip_address = IP_RE.match(ip_address)
            if ip_address:
                ip_address = ip_address.group(0)
            else:
                # no IP, probably from some dirty proxy or other device
                # throw in some bogus IP
                ip_address = '10.0.0.1'
        except IndexError:
            pass

    return ip_address


class HitCountMixin:
    """
    Mixin to evaluate a HttpRequest and a HitCount and determine whether or not
    the HitCount should be incremented and the Hit recorded.
    """

    @classmethod
    def hit_count(cls, request, hitcount):
        """
        `hit_counted` will be True if the hit was counted and False if it was
        not.  `message` will indicate by what means the Hit was either
        counted or ignored.
        """

        # as of Django 1.8.4 empty sessions are not being saved
        # https://code.djangoproject.com/ticket/25489
        if request.session.session_key is None:
            request.session.save()

        user                = request.user
        ip                  = get_ip(request)
        session_key         = request.session.session_key
        user_agent          = request.META.get('HTTP_USER_AGENT', '')[:255]
        hits_per_ip_limit   = HITCOUNT_HITS_PER_IP_LIMIT
        exclude_user_group  = EXCLUDE_USER_GROUP

        is_authenticated_user = user.is_authenticated

        # first, check our request against the IP blacklist
        if BlacklistedIP.objects.filter(ip=ip).exists():
            return {
                'hit_counted': False,
                'message': 'Not counted: user IP has been blacklisted'
            }

        # second, check our request against the user agent blacklist
        if BlacklistedUserAgent.objects.filter(user_agent=user_agent).exists():
            return {
                'hit_counted': False,
                'message': 'Not counted: user agent has been blacklisted'
            }

        # third, see if we are excluding a specific user group or not
        if exclude_user_group and is_authenticated_user:
            if user.groups.filter(name__in=exclude_user_group).exists():
                return {
                    'hit_counted': False,
                    'message': 'Not counted: user excluded by group'
                }

        # eliminated first three possible exclusions

        hits = Hit.objects.filter(hitcount=hitcount)  # get all hits related to the hitcount

        # check limit on hits from a unique ip address 
        if hits_per_ip_limit:
            if hits.filter(ip=ip).count() >= hits_per_ip_limit:
                return {
                    'hit_counted': False,
                    'message': 'Not counted: hits per ip address limit reached'
                }

        # create a Hit object with request data
        hit = Hit(
            session=session_key, 
            hitcount=hitcount, 
            ip=get_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
        )

        # first, use a user's authentication to see if they made an earlier hit
        if is_authenticated_user:
            # if not hits.filter(user=user, hitcount=hitcount):
            if not hits.filter(user=user).exists():
                hit.user = user  # associate this hit with a user
                hit.save()

                response = {
                    'hit_counted': True,
                    'message': 'Hit counted: user authentication'
                }
            else:
                response = {
                    'hit_counted': False,
                    'message': 'Not counted: Authenticated user has active hit'
                }

        # if not authenticated, see if we have a repeat session
        else:
            if not hits.filter(session=session_key).exists():
                hit.save()

                response = {
                    'hit_counted': True,
                    'message': 'Hit counted: session key'
                }
            else:
                response = {
                    'hit_counted': False,
                    'message': 'Not counted: session key has active hit'
                }

        return response


def add_hit(request, hitcount_id):
    hitcount = get_object_or_404(HitCount, id=hitcount_id)
    hit_count_response = HitCountMixin.hit_count(request, hitcount)
    
    # if hit_counted=True in the hit_count_response dict
    if hit_count_response['hit_counted']:
        return Response(hit_count_response, status=status.HTTP_201_CREATED)
    
    return Response(hit_count_response, status=status.HTTP_403_FORBIDDEN)


