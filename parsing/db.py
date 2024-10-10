from food.models import City, Restoraunt
from asgiref.sync import sync_to_async


@sync_to_async
def get_restoraunts():
    return list(Restoraunt.objects.values_list("city__slug", "slug", "id"))


@sync_to_async
def get_cities():
    return list(City.objects.all())