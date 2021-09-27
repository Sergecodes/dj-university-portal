from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = 'requested_items'

urlpatterns = [
	path('', views.RequestedItemList.as_view(), name='requested-item-list'),
	path(_('demand/'), views.RequestedItemCreate.as_view(), name='requested-item-create'),
	path(_('<int:pk>/<slug:slug>/'), views.RequestedItemDetail.as_view(), name='requested-item-detail'),
	path(_('<int:pk>/'), views.RequestedItemDetail.as_view(), name='requested-item-detail'),

]
