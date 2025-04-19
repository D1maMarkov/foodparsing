from food.models import City, Restoraunt


def get_city_by_slug(slug: str) -> City:
    return City.objects.get(slug=slug)


def get_restoraunt_by_slug(slug: str) -> Restoraunt:
    return Restoraunt.objects.get(slug=slug)
