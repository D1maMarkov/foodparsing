from django.urls import path, re_path

from food.views.api import GetDishesView, GetFilteredRestorauntsView
from food.views.templates import (
    CityFoodView,
    CityView,
    DishView,
    Index,
    PageNotFound,
    RestorauntView,
    ShopView,
)


urlpatterns = [
    path("", Index.as_view()),
    path("<city_slug>/restorany/<restoraunt_slug>/", RestorauntView.as_view()),
    path("<city_slug>/magaziny/<shop_slug>/", ShopView.as_view()),
    path("<city_slug>/restorany/<restoraunt_slug>/menu/<dish_slug>/", DishView.as_view()),
    path("<city_slug>/", CityView.as_view()),
    path("<city_slug>/<food_slug>/", CityFoodView.as_view()),
    path("api/dishes", GetDishesView.as_view()),
    path("api/restoraunts", GetFilteredRestorauntsView.as_view()),
    re_path(r".*", PageNotFound.as_view())
]
