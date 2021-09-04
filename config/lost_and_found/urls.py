from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = 'lost_and_found'

urlpatterns = [
	## LOST ITEMS ##
	path(_('lost-items/'), views.LostItemList.as_view(), name='lost-item-list'),
	path(_('lost-items/report-lost-item/'), views.LostItemCreate.as_view(), name='lost-item-create'),
	path(_('lost-items/<int:pk>/<slug:slug>/'), views.LostItemDetail.as_view(), name='lost-item-detail'),
	path(_('lost-items/<int:pk>/'), views.LostItemDetail.as_view(), name='lost-item-detail'),

	## FOUND ITEMS ##
	path(_('found-items/'), views.FoundItemList.as_view(), name='found-item-list'),
	path(_('found-items/report-found-item/'), views.FoundItemCreate.as_view(), name='found-item-create'),
	path(_('found-items/<int:pk>/<slug:slug>/'), views.FoundItemDetail.as_view(), name='found-item-detail'),
	path(_('found-items/<int:pk>/'), views.FoundItemDetail.as_view(), name='found-item-detail'),
]