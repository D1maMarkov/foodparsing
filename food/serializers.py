import random
from rest_framework import serializers

from food.models import City, CityShop, Dish, DishCategory, Food, Restoraunt, RestorauntFood, ShopCategory


class SlugField(serializers.Field):
    def to_representation(self, value: str) -> str:
        return value.replace("_", "-").lower()


class CitySerializer(serializers.ModelSerializer):
    slug = SlugField()

    class Meta:
        model = City
        fields = ['name', 'slug', 'id', 'genitive_case']


class RestorauntFoodSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = RestorauntFood
        fields = ["name", "id"]

    def get_id(self, restoraunt_food):
        return restoraunt_food.food.id

    def get_name(self, restoraunt_food):
        return restoraunt_food.food.name


class RestorauntSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    slug = SlugField()
    image_link = serializers.SerializerMethodField()

    class Meta:
        model = Restoraunt
        fields = ["slug", "name", "image", "id", "rating", "min_order", "price_category", "address", "city", "image_link", "full_address"]
    
    def get_image_link(self, restoraunt) -> str:
        dish_ids = Dish.objects.filter(restoraunt_id=restoraunt.id).values_list("id", flat=True)
        dish_id = random.choice(dish_ids)
        dish = Dish.objects.get(id=dish_id)
        return f"/media/{dish.restoraunt_id}/{dish.image.split('/')[-1]}"


class RestorauntItemSerializer(RestorauntSerializer):
    dish_categories_count = serializers.SerializerMethodField()
    dish_categories_html = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = Restoraunt
        fields = RestorauntSerializer.Meta.fields + [
            "dish_categories_count",
            "dish_categories_html",
            "full_address"
        ]

    def get_full_address(self, restoraunt) -> str:
        if restoraunt.address.startswith(restoraunt.city.name):
            return restoraunt.address
        
        return f'''{restoraunt.city.name}, {restoraunt.address}'''

    def get_dish_categories_count(self, restoraunt) -> int:
        return DishCategory.objects.filter(dishes__restoraunt_id=restoraunt.id).distinct().count()

    def get_dish_categories_html(self, restoraunt) -> str:
        categories = DishCategory.objects.filter(dishes__restoraunt_id=restoraunt.id).order_by("-id").distinct().values("name", "id")
        html = ''
        
        for category in categories:
            html += f'''&bull; &nbsp;<span data-id="{category['id']}" style="cursor: pointer;" onclick="selectFoodCategory(this, '{category['name']}')"><a style="color: rgba(var(--bs-link-color-rgb), var(--bs-link-opacity, 1));">{category['name']}</a></span><br />'''

        return html


class FoodSerializer(serializers.ModelSerializer):
    slug = SlugField()

    class Meta:
        model = Food
        fields = ["slug", "genitive_case", "name", "id"]

class DishSerializer(serializers.ModelSerializer):
    image_link = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_category(self, dish):
        return dish.category

    class Meta:
        model = Dish
        fields = [
            "name",
            "restoraunt",
            "image",
            "slug",
            "category",
            "price",
            "weight",
            "image_link"
        ]

    def get_image_link(self, dish):
        return f"/media/{dish.restoraunt_id}/{dish.image.split('/')[-1]}"


class DishCategorySerialzier(serializers.ModelSerializer):
    class Meta:
        model = DishCategory
        fields = [
            "id",
            "name",
        ]


class RestorauntHintSerialzier(serializers.ModelSerializer):
    ref = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    class Meta:
        model = Restoraunt
        fields = ["name", "ref", "address", "city"]

    def get_city(self, restoraunt: dict[str, str]) -> str:
        return restoraunt.get("city__name", "")

    def get_ref(self, restoraunt: dict[str, str]) -> str:
        return f"/{restoraunt['city__slug']}/restorany/{restoraunt['slug']}/"


class CityShopSerializer(serializers.ModelSerializer):
    slug = SlugField()
    city = CitySerializer()
    image = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    price_category = serializers.SerializerMethodField()

    class Meta:
        model = CityShop
        fields = ["shop","city","slug","rating", "image", "name", "price_category"]

    def get_price_category(self, shop) -> str:
        return shop.shop.price_category
    
    def get_image(self, shop) -> str:
        return shop.shop.image
    
    def get_name(self, shop) -> str:
        return shop.name
    
    def get_min_order(self, shop) -> str:
        return shop.min_order
    

class ShopItemSerializer(CityShopSerializer):
    product_categories_count = serializers.SerializerMethodField()
    product_categories_html = serializers.SerializerMethodField()

    class Meta:
        model = CityShop
        fields = CityShopSerializer.Meta.fields + [
            "product_categories_count",
            "product_categories_html"
        ]

    def get_product_categories_count(self, shop) -> int:
        return ShopCategory.objects.filter(products__shop_id=shop.id).distinct().count()

    def get_product_categories_html(self, shop) -> str:
        categories = ShopCategory.objects.filter(products__shop_id=shop.id).order_by("-id").distinct().values("name", "id")
        html = ''
        
        for category in categories:
            html += f'''&bull; &nbsp;<span data-id="{category['id']}" style="cursor: pointer;" onclick="selectFoodCategory(this, '{category['name']}')" ><a style="color: rgba(var(--bs-link-color-rgb), var(--bs-link-opacity, 1));">{category['name']}</a></span><br />'''

        return html