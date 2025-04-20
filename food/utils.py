from food.models import City, Restoraunt


def get_restoraunt_by_slug(slug: str) -> Restoraunt:
    return Restoraunt.objects.get(slug=slug)
