import re

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.views.generic import TemplateView

from food.models import (
    City,
    CityShop,
    Dish,
    DishCategory,
    Food,
    Restoraunt,
    RestorauntRef,
    Seo,
    Shop,
)
from food.views.api import get_dishes_context


def get_wildcard_seo(seo, wildcard_variables):
    wildcard_templates = re.findall(r"\[(.*?)\]", seo.title)
    for wildcard_template in wildcard_templates:
        obj, attr = wildcard_template.split(".")

        if not (replace_value := getattr(wildcard_variables[obj], attr)):
            replace_value = ""

        seo.title = seo.title.replace("[" + wildcard_template + "]", replace_value)
        seo.description = seo.description.replace("[" + wildcard_template + "]", replace_value)

    return seo


class Index(TemplateView):
    template_name = "food/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = City.objects.all()

        seo = Seo.objects.get(page_type="Главная")
        # print(time.time() - start)

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
        import random

        random_ids = random.sample(ids, 10)
        random_records = Restoraunt.objects.filter(id__in=random_ids)[0:8]

        context["popular_restoraunts"] = random_records

        context["restoraunts"] = Restoraunt.objects.all()[0:16]

        context["shops"] = Shop.objects.order_by("?")[0:16]

        return context


class CityView(TemplateView):
    template_name = "food/city.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get("city_slug")
        city = City.objects.get(slug=slug)
        restoraunts = Restoraunt.objects.filter(city=city)

        paginator = Paginator(restoraunts, 24)  # Show 25 contacts per page.

        page_number = self.request.GET.get("page")
        restoraunts_obj = paginator.get_page(page_number)

        foods = Food.objects.filter(city_foods__city=city)
        context["city"] = city
        context["restoraunts_obj"] = restoraunts_obj
        context["foods"] = foods

        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Город"), {"city": city})
        context["shops"] = CityShop.objects.filter(city_id=city.id)

        return context


class RestorauntView(TemplateView):
    template_name = "food/restoraunt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restoraunt_slug = kwargs.get("restoraunt_slug")
        city_slug = kwargs.get("city_slug")

        foods = Food.objects.prefetch_related("restoraunt_foods").filter(
            restoraunt_foods__restoraunt__slug=restoraunt_slug
        )

        context["foods"] = foods

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


class CityFoodView(TemplateView):
    template_name = "food/city_food.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_slug = kwargs.get("city_slug")
        food_id = kwargs.get("food_slug")

        city = City.objects.get(slug=city_slug)
        food = Food.objects.get(id=food_id)

        restoraunts = Restoraunt.objects.annotate(count=Count("foods")).filter(
            Q(city=city), Q(foods__food=food) | Q(count=0)
        )
        paginator = Paginator(restoraunts, 24)  # Show 25 contacts per page.

        page_number = self.request.GET.get("page")
        restoraunts_obj = paginator.get_page(page_number)

        context["city"] = city
        context["food"] = food
        context["foods"] = Food.objects.filter(city_foods__city=city)
        context["restoraunts_obj"] = restoraunts_obj

        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Кухня"), {"city": city, "food": food})

        return context


class DishView(TemplateView):
    template_name = "food/dish.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_slug = kwargs.get("city_slug")
        restoraunt_slug = kwargs.get("restoraunt_slug")
        dish_slug = kwargs.get("dish_slug")

        city = City.objects.get(slug=city_slug)
        restoraunt = Restoraunt.objects.filter(slug=restoraunt_slug).first()

        print(dish_slug, restoraunt)
        dish = Dish.objects.filter(slug=dish_slug, restoraunt_id=restoraunt.id).first()

        context["city"] = city
        context["restoraunt"] = restoraunt
        context["dish"] = dish

        return context
