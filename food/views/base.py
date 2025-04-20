from django.views.generic import TemplateView

from food.models import (
    City,
    Seo
)

from food.seo import get_wildcard_seo
from food.constants import FOOTER_CITY_NAMES
from functools import wraps


class ContextDecoratorMeta(type):
    def __new__(mcs, name, bases, attrs):
        if 'get_context_data' in attrs:
            original_get_context_data = attrs['get_context_data']

            @wraps(original_get_context_data)
            def wrapped_get_context_data(self, *args, **kwargs):
                context = original_get_context_data(self, *args, **kwargs)
                title = getattr(self, 'title', '')
                try:
                    context["seo"] = get_wildcard_seo(Seo.objects.get(page_type=title), context)
                except Seo.DoesNotExist:
                    context["seo"] = dict()

                footer_cities = City.objects.filter(name__in=FOOTER_CITY_NAMES)
                context["footer_cities"] = footer_cities
                request = getattr(self, "request")
                if request:
                    context["first_page_url"] = request.build_absolute_uri(request.path)
                return context

            attrs['get_context_data'] = wrapped_get_context_data
        return super().__new__(mcs, name, bases, attrs)


class BaseTemplateView(TemplateView, metaclass=ContextDecoratorMeta):
    pass