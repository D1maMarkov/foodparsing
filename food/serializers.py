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
        fields = ['name', 'slug', 'id']


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
        fields = ["slug", "name", "image", "id", "rating", "min_order", "price_category", "address", "city", "image_link"]

    def get_image_link(self) -> str:
        dish_ids = Dish.objects.filter(restoraunt_id=self.id).values_list("id", flat=True)
        dish_id = random.choice(dish_ids)
        dish = Dish.objects.get(id=dish_id)
        return dish.image_link


class RestorauntItemSerializer(RestorauntSerializer):
    dish_categories_count = serializers.SerializerMethodField()
    dish_categories_html = serializers.SerializerMethodField()

    class Meta:
        model = Restoraunt
        fields = RestorauntSerializer.Meta.fields + [
            "dish_categories_count",
            "dish_categories_html"
        ]

    def get_dish_categories_count(self) -> int:
        return DishCategory.objects.filter(dishes__restoraunt_id=self.id).distinct().count()

    def get_dish_categories_html(self) -> str:
        categories = DishCategory.objects.filter(dishes__restoraunt_id=self.id).distinct().values_list("name", flat=True)
        html = ''
        
        for category in categories:
            html += f'''&bull; &nbsp;<span style="cursor: pointer;" onclick="selectFoodCategory(this)"><a href="#" onclick="return false;">{category}</a></span><br />'''

        return html


class FoodSerializer(serializers.ModelSerializer):
    slug = SlugField()

    class Meta:
        model = Food
        fields = ["slug", "genitive_case", "name", "title"]

class DishSerializer(serializers.ModelSerializer):
    image_link = serializers.SerializerMethodField()

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

    @property
    def get_image_link(self):
        return f"/media/{self.restoraunt_id}/{self.image.split('/')[-1]}"


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

    class Meta:
        model = CityShop
        fields = ["shop","city","slug","rating", "image"]

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

    def get_product_categories_count(self) -> int:
        return ShopCategory.objects.filter(products__shop_id=self.id).distinct().count()

    def get_product_categories_html(self) -> str:
        categories = ShopCategory.objects.filter(products__shop_id=self.id).distinct().values_list("name", flat=True)
        html = ''
        
        for category in categories:
            html += f'''&bull; &nbsp;<span style="cursor: pointer;" onclick="selectFoodCategory(this)" ><a href="#" onclick="return false;">{category}</a></span><br />'''

        return html