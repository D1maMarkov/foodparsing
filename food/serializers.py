from rest_framework import serializers

from food.models import City, Dish, DishCategory, Food, Restoraunt, RestorauntFood


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
    foods = serializers.SerializerMethodField()
    dish_categories = serializers.SerializerMethodField()

    class Meta:
        model = Restoraunt
        fields = ["slug", "name", "image", "foods", "dish_categories"]

    def get_dish_categories(self, restoraunt):
        return DishCategory.objects.filter(dishes__restoraunt=restoraunt)

    def get_foods(self, restoraunt):
        return RestorauntFoodSerializer(restoraunt.foods.all(), many=True).data


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
    class Meta:
        model = Restoraunt
        fields = ["name", "id"]
