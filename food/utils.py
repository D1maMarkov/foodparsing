from food.models import City, Restoraunt


def get_city_by_slug(slug: str) -> City:
    try:
        slug = slug.replace("_", "-")
        obj = City.objects.get(slug__iexact=slug)
    except City.DoesNotExist:
        slug = slug.replace("-", "_")
        obj = City.objects.get(slug__iexact=slug)

    return obj


def get_restoraunt_by_slug(slug: str) -> Restoraunt:
    return Restoraunt.objects.get(slug__iexact=slug)
