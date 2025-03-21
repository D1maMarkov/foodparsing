import random

from rest_framework import serializers

from food.models import Dish, DishCategory, Food, Restoraunt, RestorauntFood


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
    rating = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    class Meta:
        model = Restoraunt
        fields = ["slug", "name", "image", "id", "rating", "min_order", "price_category", "address", "city"]

    def get_rating(self, restoraunt) -> str:
        return f"4.{random.randrange(5, 10)}"

    def get_city(self, restoraunt):
        return restoraunt.city


class FoodSerializer(serializers.ModelSerializer):
    restoraunts = serializers.SerializerMethodField()

    class Meta:
        model = Food
        fields = ["slug", "genitive_case", "name", "title", "restoraunts"]

    def get_restoraunts(self, food):
        return Restoraunt.objects.all()


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = "__all__"


class DishCategorySerialzier(serializers.ModelSerializer):
    class Meta:
        model = DishCategory
        fields = [
            "id",
            "name",
        ]


class RestorauntHintSerialzier(serializers.ModelSerializer):
    ref = serializers.SerializerMethodField()

    class Meta:
        model = Restoraunt
        fields = ["name", "ref", "address"]

    def get_ref(self, restoraunt: dict[str, str]) -> str:
        return f"/{restoraunt['city__slug']}/restorany/{restoraunt['slug']}/"
