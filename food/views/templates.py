import random

from django.core.paginator import Paginator
from django.db.models import Max, Q, Count, Exists, OuterRef
from django.views.generic import TemplateView

from food.interfaces import PageButton
from food.models import (
    Button,
    City,
    CityShop,
    Dish,
    Food,
    IndexPageButton,
    Restoraunt,
    RestorauntPageButton,
    RestorauntRef,
    Seo,
    ShopPageButton,
)
from food.views.api import get_dishes_context, get_shop_context

from food.seo import get_wildcard_seo
from food.constants import BLOCK_CITIES, FOOTER_CITY_NAMES, ServicesEnum


class BaseTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        footer_cities = City.objects.filter(name__in=FOOTER_CITY_NAMES)
        context["footer_cities"] = footer_cities
        return context


class Index(BaseTemplateView):
    template_name = "food/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = City.objects.filter(Exists(Restoraunt.objects.filter(city=OuterRef("pk"))))

        seo = Seo.objects.get(page_type="Главная")

        context["seo"] = seo

        context["block_cities"] = City.objects.filter(name__in=BLOCK_CITIES)

        ids = list(Restoraunt.objects.filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk")))).values_list("id", flat=True))
        
        random_ids = random.sample(ids, 8)
        random_records = Restoraunt.objects.select_related("city").filter(id__in=random_ids)[0:8]

        context["popular_restoraunts"] = random_records

        context["restoraunts"] = Restoraunt.objects.filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk")))).select_related("city").all()[0:16]

        shop_ids = CityShop.objects.annotate(max_id=Max("id"), pc=Count('products')).filter(pc__gte=1).values("shop_id", "max_id")[0:16]
        context["shops"] = (
            CityShop.objects.select_related("city", "shop").filter(id__in=[p["max_id"] for p in shop_ids]).order_by("?")
        )

        context["buttons"] = IndexPageButton.objects.all()

        return context


class CityView(BaseTemplateView):
    template_name = "food/city.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get("city_slug")
        city = City.objects.get(slug=slug)
        restoraunts = Restoraunt.objects.select_related("city").filter(city=city).filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk"))))

        paginator = Paginator(restoraunts, 24)  # Show 25 contacts per page.

        page_number = self.request.GET.get("page")
        restoraunts_obj = paginator.get_page(page_number)

        foods = Food.objects.filter(restoraunt_foods__restoraunt__city_id=city.id).distinct()
        context["city"] = city
        context["restoraunts_obj"] = restoraunts_obj
        context["foods"] = foods

        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Город"), {"city": city})
        context["shops"] = CityShop.objects.annotate(max_id=Max("id"), pc=Count('products')).filter(pc__gte=1, city_id=city.id).select_related("city", "shop")

        return context


def get_buttons(refs: list[str], default_buttons: list[PageButton]) -> list[PageButton]:
    buttons = []
    for ref in refs:
        if "market-delivery.yandex.ru" in ref:
            buttons.append(
                PageButton(
                    ref=ref,
                    text="Заказать доставку в Деливери",
                    type=ServicesEnum.delivery
                )
            )
        elif "eda.yandex.ru" in ref:
            buttons.append(
                PageButton(
                    ref=ref,
                    text="Заказать доставку в Яндекс Еда",
                    type=ServicesEnum.yandex
                )
            )
    
    for service in ServicesEnum.list():
        butt_exists = False
        for button in buttons:
            if button.type == service:
                butt_exists = True
        
        if not butt_exists:
            for default_button in default_buttons:
                if default_button.type == service:
                    buttons.append(default_button)

    return buttons


class RestorauntView(BaseTemplateView):
    template_name = "food/restoraunt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restoraunt_slug = kwargs.get("restoraunt_slug")
        city_slug = kwargs.get("city_slug")

        foods = Food.objects.filter(
            restoraunt_foods__restoraunt__slug=restoraunt_slug
        ).distinct()

        context["foods"] = foods

        dishes_context = get_dishes_context(restoraunt_slug=restoraunt_slug, city_slug=city_slug, categories=None)

        context |= dishes_context


        refs = RestorauntRef.objects.filter(restoraunt=dishes_context["restoraunt"]).values_list("ref", flat=True)
        res_buttons = RestorauntPageButton.objects.all()
        buttons = get_buttons(refs, res_buttons)
        
        context["buttons"] = buttons
        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Ресторан"), dishes_context | {"buttons": buttons})

        return context


class ShopView(BaseTemplateView):
    template_name = "food/shop.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop_slug = kwargs.get("shop_slug")
        city_slug = kwargs.get("city_slug")

        dishes_context = get_shop_context(shop_slug=shop_slug, city_slug=city_slug)

        context |= dishes_context

        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Магазин"), dishes_context)

        buttons = get_buttons([], ShopPageButton.objects.all())
        context["buttons"] = buttons

        return context


class CityFoodView(BaseTemplateView):
    template_name = "food/city_food.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_slug = kwargs.get("city_slug")
        food_id = kwargs.get("food_slug")

        city = City.objects.get(slug=city_slug)
        food = Food.objects.get(slug=food_id)

        restoraunts = (
            Restoraunt.objects.prefetch_related("foods")
            .select_related("city")
            .filter(Q(city=city, foods__food=food))
            .filter(Exists(Dish.objects.filter(restoraunt=OuterRef("pk"))))
            .distinct()
        )
        
        paginator = Paginator(restoraunts, 24)  # Show 25 contacts per page.

        page_number = self.request.GET.get("page")
        restoraunts_obj = paginator.get_page(page_number)

        context["city"] = city
        context["food"] = food
        context["foods"] = Food.objects.filter(restoraunt_foods__restoraunt__city_id=city.id).distinct()
        context["restoraunts_obj"] = restoraunts_obj

        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Кухня"), {"city": city, "food": food})

        return context


class DishView(BaseTemplateView):
    template_name = "food/dish.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_slug = kwargs.get("city_slug")
        restoraunt_slug = kwargs.get("restoraunt_slug")
        dish_slug = kwargs.get("dish_slug")

        city = City.objects.get(slug=city_slug)
        restoraunt = Restoraunt.objects.filter(slug=restoraunt_slug).first()

        dish = Dish.objects.filter(slug=dish_slug, restoraunt_id=restoraunt.id).first()

        context["city"] = city
        context["restoraunt"] = restoraunt
        context["dish"] = dish

        return context
