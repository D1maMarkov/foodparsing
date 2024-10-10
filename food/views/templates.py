from django.views.generic import TemplateView
from food.models import City, Dish, DishCategory, Food, Restoraunt, Seo
from django.db.models import Count


def get_wildcard_seo(seo, wildcard_variables):
    wildcard_templates = re.findall(r'\[(.*?)\]', seo.title)
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
        
        context["seo"] = seo

        return context

import re

class CityView(TemplateView):
    template_name = "food/city.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('city_slug')
        city = City.objects.get(slug=slug)
        restoraunts = Restoraunt.objects.filter(city=city)
        foods = Food.objects.filter(city_foods__city=city)
        context["city"] = city
        context["restoraunts"] = restoraunts
        context["foods"] = foods
        
        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Город"), {"city": city})

        return context


class RestorauntView(TemplateView):
    template_name = "food/restoraunt.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restoraunt_slug = kwargs.get('restoraunt_slug')
        city_slug = kwargs.get('city_slug')
        
        restoraunt = Restoraunt.objects.get(slug=restoraunt_slug, city__slug=city_slug)
        foods = Food.objects.filter(restoraunt_foods__restoraunt=restoraunt)
        dish_categories = DishCategory.objects.annotate(count=Count("name")).filter(dishes__restoraunt=restoraunt)
        dishes = Dish.objects.filter(restoraunt=restoraunt)

        context["restoraunt"] = restoraunt
        context["foods"] = foods
        context["dish_categories"] = dish_categories
        context["dishes"] = dishes
        context["seo"] = get_wildcard_seo(Seo.objects.get(page_type="Ресторан"), {
            "city": restoraunt.city,
            "restoraunt": restoraunt
        })
        return context

class CityFoodView(TemplateView):
    template_name = "food/city_food.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_slug = kwargs.get('city_slug')
        food_slug = kwargs.get('food_slug')
        
        city = City.objects.get(slug=city_slug)
        food = Food.objects.get(slug=food_slug)

        context['city'] = city
        context['food'] = food
        context['foods'] = Food.objects.filter(city_foods__city=city)
        context['restoraunts'] = Restoraunt.objects.filter(foods__food=food)
        return context