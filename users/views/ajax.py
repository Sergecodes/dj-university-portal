import datetime
import json
import mimetypes
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.views.decorators.http import require_GET

User = get_user_model()


@require_GET
def check_username(request):
   print(request.GET)
   username = request.GET.get('username', '')
   if username:
      taken = User.objects.filter(username=username).exists()
      return JsonResponse({ 'available': not taken })
   
   return JsonResponse({'message': 'Empty username'}, status=400)
