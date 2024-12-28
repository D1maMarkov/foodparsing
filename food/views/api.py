from django.db.models import Count, Q
from django.http import HttpRequest, JsonResponse
from django.template import loader
from django.views import View

from food.models import City, Dish, DishCategory, Restoraunt
from food.serializers import RestorauntHintSerialzier


def get_dishes_context(restoraunt_slug, city_slug, categories):
    city = City.objects.get(slug=city_slug)
    restoraunt = Restoraunt.objects.get(city_id=city.id, slug=restoraunt_slug)

    category_ids = list(map(int, categories.split(","))) if categories else None
    query = Q()

    query &= Q(dishes__restoraunt_id=restoraunt)

    if categories:
        query &= Q(id__in=category_ids)

    categories = DishCategory.objects.annotate(count=Count("name")).filter(query).order_by("-id")

    dishes_query = Dish.objects.filter(restoraunt_id=restoraunt.id)

    return {"dishes": dishes_query, "dish_categories": categories, "city": city, "restoraunt": restoraunt}


class GetDishesView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        restoraunt_slug = request.GET.get("restoraunt")
        categories = request.GET.get("categories")
        city_slug = request.GET.get("city")

        dishes_context = get_dishes_context(restoraunt_slug=restoraunt_slug, city_slug=city_slug, categories=categories)

        return JsonResponse({"content": loader.render_to_string(f"food/restoraunt-content.html", dishes_context, None)})


class GetFilteredRestorauntsView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        restoraunt_name_starts_with = request.GET.get("restoraunt_name")
        restoraunts = Restoraunt.objects.filter(name__istartswith=restoraunt_name_starts_with).values("id", "name")[
            0:10
        ]

        return JsonResponse({"restorunts": RestorauntHintSerialzier(restoraunts, many=True).data})
