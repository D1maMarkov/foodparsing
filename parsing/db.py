from asgiref.sync import sync_to_async
from django.db.models import Count

from food.models import City, CityShop, Restoraunt, Shop


@sync_to_async
def get_restoraunts():
    # return list(
    #    Restoraunt.objects.annotate(count=Count("foods")).filter(count=0)
    #    .values_list("city__slug", "slug", "id")
    # )
    return list(
        Restoraunt.objects.filter(slug="sushi_lend_hd7jq", city__slug="Georgievsk").values_list(
            "city__slug", "slug", "id"
        )
    )


@sync_to_async
def get_cities():
    return list(City.objects.all())


@sync_to_async
def get_shops():
    return list(Shop.objects.all())


@sync_to_async
def get_city_shops():
    return list(
        CityShop.objects.annotate(count=Count("products")).filter(count=0).values("city__slug", "id", "slug", "city_id")
    )
