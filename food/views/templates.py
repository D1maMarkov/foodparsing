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
    ShopProduct,
)
from food.serializers import CitySerializer, CityShopSerializer, FoodSerializer, RestorauntSerializer
from food.views.api import get_dishes_context, get_shop_context

from food.constants import BLOCK_CITIES
from food.views.base import BaseTemplateView


class Index(BaseTemplateView):
    template_name = "food/index.html"
    title = "Главная"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_cities = City.objects.filter(Exists(Restoraunt.objects.filter(have_dishes=True, city=OuterRef("pk"))))
        block_cities = City.objects.filter(name__in=BLOCK_CITIES)

        serialized_cities = CitySerializer(all_cities, many=True).data
        context["cities"] = serialized_cities
        context["block_cities"] = CitySerializer(block_cities, many=True).data

        random_cities = random.sample(serialized_cities, 16)
        restoraunts = []
        for city in random_cities:
            if len(restoraunts) >= 8:
                break
            r = Restoraunt.objects.select_related('city').filter(city_id=city["id"]).filter(~Q(image_link__isnull=True)).order_by("?").first()
            if r:
                restoraunts.append(r)
        
        random_cities = random.sample(serialized_cities, 16)

        popular_restoraunts = []
        for city in random_cities:
            if len(popular_restoraunts) >= 8:
                break
            r = Restoraunt.objects.select_related('city').filter(city_id=city["id"]).filter(~Q(image_link__isnull=True)).order_by("?").first()
            if r:
                popular_restoraunts.append(r)

        context["popular_restoraunts"] = RestorauntSerializer(popular_restoraunts, many=True).data

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
        slug = kwargs.get("city_slug")
        city = City.objects.get(slug=slug)
        
        restoraunts = (
            Restoraunt.objects.select_related("city")
            .filter(have_dishes=True, city=city)
            .order_by('-image_link')
        )

        paginator = Paginator(restoraunts, 24)

        page_number = self.request.GET.get("page")
        restoraunts_obj = paginator.get_page(page_number)
        restoraunts_obj.object_list = RestorauntSerializer(restoraunts_obj.object_list, many=True).data

        foods = Food.objects.filter(restoraunt_foods__restoraunt__city_id=city.id).distinct()
        context["city"] = CitySerializer(city).data
        context["restoraunts_obj"] = restoraunts_obj
        context["foods"] = FoodSerializer(foods, many=True).data

        #shops = CityShop.objects.annotate(max_id=Max("id"), pc=Count('products')).filter(pc__gte=1, city_id=city.id).select_related("city", "shop")
        shops = CityShop.objects.filter(Exists(ShopProduct.objects.filter(shop=OuterRef('pk'))), city=city).select_related("city", "shop")

        context["shops"] = CityShopSerializer(shops, many=True).data
        context["buttons"] = IndexPageButton.objects.all()

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

        refs = RestorauntRef.objects.filter(restoraunt=dishes_context["restoraunt"]["id"])
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
        city_slug = kwargs.get("city_slug")
        food_id = kwargs.get("food_slug")

        city = City.objects.get(slug=city_slug)
        food = Food.objects.get(slug=food_id)

        restoraunts = (
            Restoraunt.objects.prefetch_related("foods")
            .select_related("city")
            .filter(city=city, foods__food=food)
            .filter(have_dishes=True)
            .distinct()
            .order_by('-image_link')
        )

        paginator = Paginator(restoraunts, 24)

        page_number = self.request.GET.get("page")
        restoraunts_obj = paginator.get_page(page_number)
        restoraunts_obj.object_list = RestorauntSerializer(restoraunts_obj.object_list, many=True).data

        foods = Food.objects.filter(restoraunt_foods__restoraunt__city_id=city.id).distinct()

        context["city"] = CitySerializer(city).data
        context["food"] = FoodSerializer(food).data
        context["foods"] = FoodSerializer(foods, many=True).data
        context["restoraunts_obj"] = restoraunts_obj
        context["buttons"] = IndexPageButton.objects.all()

        return context


class DishView(BaseTemplateView):
    template_name = "food/dish.html"
    title = "Блюдо"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_slug = kwargs.get("city_slug")
        restoraunt_slug = kwargs.get("restoraunt_slug")
        dish_slug = kwargs.get("dish_slug")

        city = City.objects.get(slug=city_slug)
        restoraunt = Restoraunt.objects.filter(slug=restoraunt_slug).first()

        dish = Dish.objects.filter(slug=dish_slug, restoraunt_id=restoraunt.id).first()

        context["city"] = CitySerializer(city).data
        context["restoraunt"] = RestorauntSerializer(restoraunt).data
        context["dish"] = dish

        return context


class PageNotFound(BaseTemplateView):
    template_name = "food/404.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)