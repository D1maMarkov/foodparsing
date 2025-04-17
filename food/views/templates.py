import random
from typing import Any

from django.core.paginator import Paginator
from django.db.models import Max, Q, Count, Exists, OuterRef

from food.get_buttons import get_buttons
from food.models import (
    City,
    CityShop,
    Dish,
    Food,
    IndexPageButton,
    Restoraunt,
    RestorauntPageButton,
    RestorauntRef,
    ShopPageButton,
)
from food.serializers import CitySerializer, CityShopSerializer, FoodSerializer, RestorauntSerializer
from food.utils import get_city_by_slug
from food.views.api import get_dishes_context, get_shop_context

from food.constants import BLOCK_CITIES
from food.views.base import BaseTemplateView


class Index(BaseTemplateView):
    template_name = "food/index.html"
    title = "Главная"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_cities = City.objects.filter(Exists(Restoraunt.objects.filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk"))), city=OuterRef("pk"))))
        block_cities = City.objects.filter(name__in=BLOCK_CITIES)

        context["cities"] = CitySerializer(all_cities, many=True).data
        context["block_cities"] = CitySerializer(block_cities, many=True).data

        ids = list(Restoraunt.objects.filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk")))).values_list("id", flat=True))
        
        random_ids = random.sample(ids, 8)
        random_records = Restoraunt.objects.select_related("city").filter(id__in=random_ids)[0:8]
        restoraunts = Restoraunt.objects.filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk")))).select_related("city").all()[0:16]

        context["popular_restoraunts"] = RestorauntSerializer(random_records, many=True).data

        context["restoraunts"] = RestorauntSerializer(restoraunts, many=True).data

        shop_ids = CityShop.objects.annotate(max_id=Max("id"), pc=Count('products')).filter(pc__gte=1).values("shop_id", "max_id")[0:16]
        shops = CityShop.objects.select_related("city", "shop").filter(id__in=[p["max_id"] for p in shop_ids]).order_by("?")
        
        context["shops"] = CityShopSerializer(shops, many=True).data

        context["buttons"] = IndexPageButton.objects.all()

        return context


class CityView(BaseTemplateView):
    template_name = "food/city.html"
    title = "Город"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        slug = kwargs.get("city_slug").lower()
        city = get_city_by_slug(slug)
        
        restoraunts = Restoraunt.objects.select_related("city").filter(city=city).filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk"))))
        serialized_restoraunts = RestorauntSerializer(restoraunts, many=True).data

        paginator = Paginator(serialized_restoraunts, 24)  # Show 25 contacts per page.

        page_number = self.request.GET.get("page")
        restoraunts_obj = paginator.get_page(page_number)

        foods = Food.objects.filter(restoraunt_foods__restoraunt__city_id=city.id).distinct()
        context["city"] = CitySerializer(city).data
        context["restoraunts_obj"] = restoraunts_obj
        context["foods"] = FoodSerializer(foods, many=True).data

        shops = CityShop.objects.annotate(max_id=Max("id"), pc=Count('products')).filter(pc__gte=1, city_id=city.id).select_related("city", "shop")

        context["shops"] = CityShopSerializer(shops, many=True).data

        return context


class RestorauntView(BaseTemplateView):
    template_name = "food/restoraunt.html"
    title = "Ресторан"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restoraunt_slug = kwargs.get("restoraunt_slug")
        city_slug = kwargs.get("city_slug")

        foods = Food.objects.filter(
            restoraunt_foods__restoraunt__slug=restoraunt_slug
        ).distinct()

        context["foods"] = FoodSerializer(foods, many=True).data

        dishes_context = get_dishes_context(restoraunt_slug=restoraunt_slug, city_slug=city_slug, categories=None)

        context |= dishes_context

        refs = RestorauntRef.objects.filter(restoraunt=dishes_context["restoraunt"])
        res_buttons = RestorauntPageButton.objects.all()
        buttons = get_buttons(refs, res_buttons)

        context["buttons"] = buttons

        return context


class ShopView(BaseTemplateView):
    template_name = "food/shop.html"
    title = "Магазин"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop_slug = kwargs.get("shop_slug").replace("-", "_")
        city_slug = kwargs.get("city_slug")

        dishes_context = get_shop_context(shop_slug=shop_slug, city_slug=city_slug)

        context |= dishes_context

        buttons = get_buttons([], ShopPageButton.objects.all())
        context["buttons"] = buttons

        return context


class CityFoodView(BaseTemplateView):
    template_name = "food/city_food.html"
    title = "Кухня"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_slug = kwargs.get("city_slug").replace("-", "_")
        food_id = kwargs.get("food_slug")

        city = get_city_by_slug(city_slug)
        food = Food.objects.get(slug=food_id)

        restoraunts = (
            Restoraunt.objects.prefetch_related("foods")
            .select_related("city")
            .filter(Q(city=city, foods__food=food))
            .filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk"))))
            .distinct()
        )
        serialized_restoraunts = RestorauntSerializer(restoraunts, many=True).data

        paginator = Paginator(serialized_restoraunts, 24)

        page_number = self.request.GET.get("page")
        restoraunts_obj = paginator.get_page(page_number)

        foods = Food.objects.filter(restoraunt_foods__restoraunt__city_id=city.id).distinct()

        context["city"] = CitySerializer(city).data
        context["food"] = FoodSerializer(food).data
        context["foods"] = FoodSerializer(foods, many=True).data
        context["restoraunts_obj"] = restoraunts_obj

        return context


class DishView(BaseTemplateView):
    template_name = "food/dish.html"
    title = "Блюдо"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_slug = kwargs.get("city_slug")
        restoraunt_slug = kwargs.get("restoraunt_slug")
        dish_slug = kwargs.get("dish_slug").replace("-", "_")

        city = get_city_by_slug(city_slug)
        restoraunt = Restoraunt.objects.filter(slug=restoraunt_slug).first()

        dish = Dish.objects.filter(slug=dish_slug, restoraunt_id=restoraunt.id).first()

        context["city"] = CitySerializer(city).data
        context["restoraunt"] = RestorauntSerializer(restoraunt).data
        context["dish"] = dish

        return context
