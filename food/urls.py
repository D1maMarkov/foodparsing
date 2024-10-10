from django.urls import path
from parsing.views import parse_cities_view, parse_foods_view, parse_restoraunt_foods, parse_dishes_view, parse_restoraunts_view
from food.views.templates import CityFoodView, Index, CityView, RestorauntView


urlpatterns = [
    path('', Index.as_view()),
    path('<city_slug>/place/<restoraunt_slug>/', RestorauntView.as_view()),
    path('parse/restoraunt-foods', parse_restoraunt_foods),
    path('parse/cities', parse_cities_view),
    path('parse/foods', parse_foods_view),
    path('parse/restoraunts', parse_restoraunts_view),
    path('parse/dishes', parse_dishes_view),
    path('<city_slug>/', CityView.as_view()),
    path('<city_slug>/<food_slug>/', CityFoodView.as_view()),
]
