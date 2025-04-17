from django.contrib import admin

from food.models import (
    City,
    CityShop,
    Dish,
    DishCategory,
    DishRef,
    Food,
    IndexPageButton,
    RestorauntPageButton,
    ShopPageButton,
    Restoraunt,
    RestorauntFood,
    RestorauntRef,
    Seo,
    Shop,
    ShopProduct,
)


class CityAdmin(admin.ModelAdmin):
    search_fields = ["slug", "name"]


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


class CityShopAdmin(admin.ModelAdmin):
    search_fields = ["slug"]


class DishRefInline(admin.StackedInline):
    extra = 0
    model = DishRef


class DishAdmin(admin.ModelAdmin):
    inlines = [DishRefInline]
    list_display = ["name", "restoraunt"]
    readonly_fields = ["restoraunt", "category"]


class ShopAdmin(admin.ModelAdmin):
    ordering = ["name"]


class SeoAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "SEO",
            {
                "fields": [
                    "page_type",
                    "title",
                    "h1",
                    "description",
                    "text",
                ],
                "description": "Доступны подстановочные шаблоны:" 
                + "<br><code>[city.name]</code>"
                + "<br><code>[city.title]</code>"
                + "<br><code>[city.genitive_case]</code>"

                + "<br><code>[food.name]</code>"
                + "<br><code>[food.genitive_case]</code>"

                + "<br><code>[restoraunt.name]</code>"
                + "<br><code>[restoraunt.owner]</code>"
                + "<br><code>[restoraunt.address]</code>"
                + "<br><code>[restoraunt.full_address]</code>"
                + "<br><code>[restoraunt.price_category]</code>"
                + "<br><code>[restoraunt.rating]</code>"
                + "<br><code>[restoraunt.min_order]</code>"
                + "<br><code>[restoraunt.dish_categories_count]</code>"
                + "<br><code>[restoraunt.dish_categories_html]</code>"

                + "<br><code>[dish.name]</code>"
                + "<br><code>[dish.price]</code>"
                + "<br><code>[dish.weight]</code>"

                + "<br><code>[shop.name]</code>"
                + "<br><code>[shop.address]</code>"
                + "<br><code>[shop.min_order]</code>"
                + "<br><code>[shop.price_category]</code>"
                + "<br><code>[shop.product_categories_count]</code>"
                + "<br><code>[shop.product_categories_html]</code>"
                + "<br><code>[current_date]</code>"
                + "<br><code>[button.delivery]</code>"
                + "<br><code>[button.yandex]</code>"
                + "<br><code>[link_mobile.delivery]</code>"
                + "<br><code>[link_mobile.yandex]</code>",
            },
        ),
    ]

admin.site.register(Dish, DishAdmin)
admin.site.register(DishCategory, DishCategoryAdmin)
admin.site.register(Restoraunt, RestourantAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(CityShop, CityShopAdmin)
admin.site.register(Seo, SeoAdmin)
admin.site.register(ShopProduct)
admin.site.register(IndexPageButton)
admin.site.register(RestorauntPageButton)
admin.site.register(ShopPageButton)
admin.site.register(RestorauntFood)
