from django.contrib import admin

from food.models import (
    City,
    CityShop,
    Dish,
    DishCategory,
    DishRef,
    Food,
    IndexPageButton,
    Restoraunt,
    RestorauntFood,
    RestorauntRef,
    Seo,
    Shop,
    ShopProduct,
)


class CityAdmin(admin.ModelAdmin):
    pass


class FoodAdmin(admin.ModelAdmin):
    pass


class DishInline(admin.StackedInline):
    model = Dish
    extra = 0
    # fields = ["name", "price", "weight"]
    raw_id_fields = ["category"]
    exclude = ["unique_key"]


class CityFoodAdmin(admin.ModelAdmin):
    pass


class RestorauntRefInline(admin.StackedInline):
    model = RestorauntRef
    extra = 0


class RestourantAdmin(admin.ModelAdmin):
    inlines = [RestorauntRefInline, DishInline]
    search_fields = ["slug"]


class DishCategoryAdmin(admin.ModelAdmin):
    pass


class DishRefInline(admin.StackedInline):
    extra = 0
    model = DishRef


class DishAdmin(admin.ModelAdmin):
    inlines = [DishRefInline]
    list_display = ["name", "restoraunt"]
    readonly_fields = ["restoraunt", "category"]


class ShopAdmin(admin.ModelAdmin):
    ordering = ["name"]


admin.site.register(Dish, DishAdmin)
admin.site.register(DishCategory, DishCategoryAdmin)
admin.site.register(Restoraunt, RestourantAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(CityShop)
admin.site.register(Seo)
admin.site.register(ShopProduct)
admin.site.register(IndexPageButton)
admin.site.register(RestorauntFood)
