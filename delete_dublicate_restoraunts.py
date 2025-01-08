from food.models import Restoraunt
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


class RestorauntInterface:
    def __init__(self, slug, city_id, id):
        self.city_id = city_id
        self.slug = slug
        self.id = id

    def __hash__(self):
        return hash((self.slug, self.city_id))

    def __eq__(self, other):
        return self.city_id == other.city_id and self.slug == other.slug


restoraunts = [
    RestorauntInterface(city_id=r["city_id"], id=r["id"], slug=r["slug"])
    for r in Restoraunt.objects.values("city_id", "slug", "id")
][::-1]

ids = [r.id for r in restoraunts]
set_ids = [r.id for r in set(restoraunts)]

ids_to_delete = set(ids) - set(set_ids)

Restoraunt.objects.filter(id__in=ids_to_delete).delete()
