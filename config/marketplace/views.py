from django.shortcuts import render
from django.views import generic
from .models import Item


# site index view
def index(request):
    # get and sort items based on owner's points and creation date*
    latest_items = Item.objects.select_related('owner')\
        .order_by('-date_added', 'owner__reputation')

    return render(request, 'index.html', {latest_items: latest_items})


class ItemList(generic.ListView):
    model = Item
    paginate_by = 5


class ItemDetail(generic.DetailView):
    model = Item
