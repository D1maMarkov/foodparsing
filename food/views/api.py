from typing import Any
from django.db.models import Q, Exists, OuterRef
from django.http import HttpRequest, JsonResponse
from django.template import loader
from django.views import View

from food.models import City, CityShop, Dish, DishCategory, Restoraunt, ShopCategory
from food.serializers import CitySerializer, DishSerializer, RestorauntHintSerialzier, RestorauntItemSerializer, ShopItemSerializer


def get_dishes_context(restoraunt_slug, city_slug, categories) -> dict[str, Any]:
    city = City.objects.get(slug=city_slug)
    restoraunt = Restoraunt.objects.get(city_id=city.id, slug=restoraunt_slug)

    category_ids = list(map(int, categories.split(","))) if categories else None
    query = Q()

    query &= Q(dishes__restoraunt_id=restoraunt)

    if categories:
        query &= Q(id__in=category_ids)

    categories = list(DishCategory.objects.filter(query).order_by("-id").distinct())

    dishes = Dish.objects.select_related("category").filter(restoraunt_id=restoraunt.id)

    return {
        "dishes": DishSerializer(dishes, many=True).data, 
        "dish_categories": categories,
        "city": CitySerializer(city).data, 
        "restoraunt": RestorauntItemSerializer(restoraunt, context={"categories": categories}).data
    }


def get_shop_context(shop_slug, city_slug) -> dict[str, Any]:
    city = City.objects.get(slug=city_slug)

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
