from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = 'requested_items'


urlpatterns = [
	path('', views.RequestedItemList.as_view(), name='requested-item-list'),
	path(_('request-item/'), views.RequestedItemCreate.as_view(), name='requested-item-create'),
	path(_('<int:pk>/edit/'), views.RequestedItemUpdate.as_view(), name='requested-item-update'),
	path(_('<int:pk>/delete/'), views.RequestedItemDelete.as_view(), name='requested-item-delete'),
	path(_('<int:pk>/<slug:slug>/'), views.RequestedItemDetail.as_view(), name='requested-item-detail'),
	path('<int:pk>/', views.RequestedItemDetail.as_view(), name='requested-item-detail'),

]
