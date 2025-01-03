from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.template import loader
from django.views import View

from food.models import City, CityShop, Dish, DishCategory, Restoraunt, ShopCategory
from food.serializers import RestorauntHintSerialzier


def get_dishes_context(restoraunt_slug, city_slug, categories):
    city = City.objects.get(slug=city_slug)
    restoraunt = Restoraunt.objects.get(city_id=city.id, slug=restoraunt_slug)

    category_ids = list(map(int, categories.split(","))) if categories else None
    query = Q()

    query &= Q(dishes__restoraunt_id=restoraunt)

    if categories:
        query &= Q(id__in=category_ids)

    categories = DishCategory.objects.filter(query).order_by("-id")

    dishes_query = Dish.objects.select_related("category").filter(restoraunt_id=restoraunt.id)

    return {"dishes": dishes_query, "dish_categories": categories, "city": city, "restoraunt": restoraunt}


def get_shop_context(shop_slug, city_slug):
    city = City.objects.get(slug=city_slug)

    shop = CityShop.objects.get(city_id=city.id, slug=shop_slug)

    query = Q()

    query &= Q(products__shop_id=shop)

    categories = ShopCategory.objects.filter(query).order_by("-id")

    products_query = shop.products.all()

    return {"products": products_query, "shop_categories": categories, "city": city, "shop": shop}


class GetDishesView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        restoraunt_slug = request.GET.get("restoraunt")
        categories = request.GET.get("categories")
        city_slug = request.GET.get("city")

        dishes_context = get_dishes_context(restoraunt_slug=restoraunt_slug, city_slug=city_slug, categories=categories)

        return JsonResponse({"content": loader.render_to_string("food/restoraunt-content.html", dishes_context, None)})


class GetFilteredRestorauntsView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        restoraunt_name_starts_with = request.GET.get("restoraunt_name")
        restoraunts = Restoraunt.objects.filter(name__istartswith=restoraunt_name_starts_with).values(
            "slug", "city__slug", "name"
        )[0:10]

        return JsonResponse({"restoraunts": RestorauntHintSerialzier(restoraunts, many=True).data})
