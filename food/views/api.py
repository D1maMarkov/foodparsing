from typing import Any
from django.db.models import Q, Exists, OuterRef
from django.http import HttpRequest, JsonResponse
from django.template import loader
from django.views import View

from food.models import CityShop, Dish, DishCategory, Restoraunt, ShopCategory
from food.serializers import CitySerializer, RestorauntHintSerialzier, RestorauntItemSerializer, ShopItemSerializer
from food.utils import get_city_by_slug


def get_dishes_context(restoraunt_slug, city_slug, categories) -> dict[str, Any]:
    city = get_city_by_slug(city_slug)
    restoraunt = Restoraunt.objects.get(city_id=city.id, slug=restoraunt_slug)

    category_ids = list(map(int, categories.split(","))) if categories else None
    query = Q()

    query &= Q(dishes__restoraunt_id=restoraunt)

    if categories:
        query &= Q(id__in=category_ids)

    categories = DishCategory.objects.filter(query).order_by("-id").distinct()

    dishes_query = Dish.objects.select_related("category").filter(restoraunt_id=restoraunt.id)

    return {
        "dishes": dishes_query, 
        "dish_categories": categories,
        "city": CitySerializer(city).data, 
        "restoraunt": RestorauntItemSerializer(restoraunt).data
    }


def get_shop_context(shop_slug, city_slug) -> dict[str, Any]:
    city = get_city_by_slug(city_slug)

    shop = CityShop.objects.select_related('shop').get(city_id=city.id, slug=shop_slug)

    query = Q()

    query &= Q(products__shop_id=shop)

    categories = ShopCategory.objects.filter(query).order_by("-id").distinct()

    products_query = shop.products.all()

    return {
        "products": products_query, 
        "shop_categories": categories, 
        "city": CitySerializer(city).data, 
        "shop": ShopItemSerializer(shop).data
    }


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
        restoraunts = Restoraunt.objects.filter(name__istartswith=restoraunt_name_starts_with).filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk")))).values(
            "slug", "city__slug", "city__name", "name", "address"
        )[0:10]

        return JsonResponse({"restoraunts": RestorauntHintSerialzier(restoraunts, many=True).data})
