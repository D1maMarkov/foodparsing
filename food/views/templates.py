import random
import re

from django.core.paginator import Paginator
from django.db.models import Max, Q
from django.views.generic import TemplateView

from food.models import (
    City,
    CityShop,
    Dish,
    Food,
    IndexPageButton,
    Restoraunt,
    RestorauntRef,
    Seo,
)
from food.views.api import get_dishes_context, get_shop_context


def get_wildcard_seo(seo, wildcard_variables):
    wildcard_templates = re.findall(r"\[(.*?)\]", seo.title)
    for wildcard_template in wildcard_templates:
        obj, attr = wildcard_template.split(".")

        if not (replace_value := getattr(wildcard_variables[obj], attr)):
            replace_value = ""

        seo.title = seo.title.replace("[" + wildcard_template + "]", replace_value)
        seo.description = seo.description.replace("[" + wildcard_template + "]", replace_value)

    return seo


class BaseTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        footer_city_names = [
            "Москва",
            "Санкт-Петербург",
            "Нижний Новгород",
            "Екатеринбург",
            "Казань",
            "Краснодар",
            "Ростов-на-Дону",
            "Уфа",
            "Саратов",
            "Иркутск",
            "Красноярск",
            "Новосибирск",
        ]

        footer_cities = City.objects.filter(name__in=footer_city_names)

        context["footer_cities"] = footer_cities
        return context


class Index(BaseTemplateView):
    template_name = "food/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = City.objects.all()

        seo = Seo.objects.get(page_type="Главная")

        context["seo"] = seo
        block_cities = [
            "Москва",
            "Санкт-Петербург",
            "Новосибирск",
            "Екатеринбург",
            "Казань",
            "Красноярск",
            "Нижний Новгород",
            "Челябинск",
        ]

        context["block_cities"] = City.objects.filter(name__in=block_cities)

        ids = list(Restoraunt.objects.values_list("id", flat=True))

        random_ids = random.sample(ids, 10)
        random_records = Restoraunt.objects.select_related("city").filter(id__in=random_ids)[0:8]

        context["popular_restoraunts"] = random_records

        context["restoraunts"] = Restoraunt.objects.select_related("city").all()[0:16]

        shop_ids = CityShop.objects.values("shop_id").annotate(max_id=Max("id"))[0:16]
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
        restoraunts = Restoraunt.objects.select_related("city").filter(city=city)

        paginator = Paginator(restoraunts, 24)  # Show 25 contacts per page.

        page_number = self.request.GET.get("page")
        restoraunts_obj = paginator.get_page(page_number)

        foods = Food.objects.filter(restoraunt_foods__restoraunt__city_id=city.id).distinct()
        context["city"] = city
        context["restoraunts_obj"] = restoraunts_obj
        context["foods"] = foods

        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Город"), {"city": city})
        context["shops"] = CityShop.objects.select_related("city", "shop").filter(city_id=city.id)

        return context


class RestorauntView(BaseTemplateView):
    template_name = "food/restoraunt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restoraunt_slug = kwargs.get("restoraunt_slug")
        city_slug = kwargs.get("city_slug")

        """foods = Food.objects.filter(
            restoraunt_foods__restoraunt__slug=restoraunt_slug
        ).distinct()

        context["foods"] = foods"""

        dishes_context = get_dishes_context(restoraunt_slug=restoraunt_slug, city_slug=city_slug, categories=None)

        context |= dishes_context

        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Ресторан"), dishes_context)

        refs = RestorauntRef.objects.filter(restoraunt=dishes_context["restoraunt"]).values_list("ref", flat=True)
        refs_dict = {}
        for ref in refs:
            if "market-delivery.yandex.ru" in ref:
                refs_dict["Деливери"] = refs_dict.get("Деливери", []) + [ref]
            elif "eda.yandex.ru" in ref:
                refs_dict["Яндекс Еда"] = refs_dict.get("Яндекс Еда", []) + [ref]
            elif "kuper.ru" in ref:
                refs_dict["Сбер Купер"] = refs_dict.get("Сбер Купер", []) + [ref]

        context["refs"] = refs_dict

        return context


class ShopView(BaseTemplateView):
    template_name = "food/shop.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop_slug = kwargs.get("shop_slug")
        city_slug = kwargs.get("city_slug")

        dishes_context = get_shop_context(shop_slug=shop_slug, city_slug=city_slug)

        context |= dishes_context

        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Ресторан"), dishes_context)

        """refs = RestorauntRef.objects.filter(restoraunt=dishes_context["restoraunt"]).values_list("ref", flat=True)
        refs_dict = {}
        for ref in refs:
            if "market-delivery.yandex.ru" in ref:
                refs_dict["Деливери"] = refs_dict.get("Деливери", []) + [ref]
            elif "eda.yandex.ru" in ref:
                refs_dict["Яндекс Еда"] = refs_dict.get("Яндекс Еда", []) + [ref]
            elif "kuper.ru" in ref:
                refs_dict["Сбер Купер"] = refs_dict.get("Сбер Купер", []) + [ref]

        context["refs"] = refs_dict"""

        return context


class CityFoodView(BaseTemplateView):
    template_name = "food/city_food.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_slug = kwargs.get("city_slug")
        food_id = kwargs.get("food_slug")

        city = City.objects.get(slug=city_slug)
        food = Food.objects.get(id=food_id)

        restoraunts = (
            Restoraunt.objects.prefetch_related("foods").select_related("city").filter(Q(city=city, foods__food=food))
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
