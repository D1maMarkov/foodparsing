from django.contrib import admin
from food.models import City, CityFood, Dish, DishCategory, Food, Restoraunt, RestorauntDish, RestorauntFood, Seo


class CityAdmin(admin.ModelAdmin):
    pass


class FoodAdmin(admin.ModelAdmin):
    pass


class CityFoodAdmin(admin.ModelAdmin):
    pass


class RestourantAdmin(admin.ModelAdmin):
    pass


class DishCategoryAdmin(admin.ModelAdmin):
    pass


class DishAdmin(admin.ModelAdmin):
    list_display = ["name", "restoraunt"]


admin.site.register(Dish, DishAdmin)
admin.site.register(DishCategory, DishCategoryAdmin)
admin.site.register(Restoraunt, RestourantAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Food, FoodAdmin)
#admin.site.register(CityFood, CityFoodAdmin)
#admin.site.register(RestorauntFood)
admin.site.register(Seo)