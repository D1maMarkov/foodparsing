from rest_framework import serializers

from food.models import City, Dish, DishCategory, Food, Restoraunt, RestorauntFood


class RestorauntFoodSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = RestorauntFood
        fields = [
            "name",
            "id"
        ]

    def get_id(self, restoraunt_food):
        return restoraunt_food.food.id
    
    def get_name(self, restoraunt_food):
        return restoraunt_food.food.name

class RestorauntSerializer(serializers.ModelSerializer):
    foods = serializers.SerializerMethodField()
    dish_categories = serializers.SerializerMethodField()

    class Meta:
        model = Restoraunt
        fields = [
            "slug",
            "name",
            "image",
            "foods",
            "dish_categories"
        ]
    def get_dish_categories(self, restoraunt):
        return DishCategory.objects.filter(dishes__restoraunt=restoraunt)
        
    def get_foods(self, restoraunt):
        return RestorauntFoodSerializer(restoraunt.foods.all(), many=True).data


class CitySerializer(serializers.ModelSerializer):
    foods = serializers.SerializerMethodField()
    restoraunts = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = [
            "slug",
            "foods",
            "restoraunts",
            "genitive_case"
        ]
        
    def get_foods(self, city):
        foods_ids = city.foods.select_related("food").values_list("food", flat=True).all()
        foods = Food.objects.filter(id__in=foods_ids)

        return foods

    def get_restoraunts(self, city):
        return RestorauntSerializer(city.restoraunts.all(), many=True).data
    
    
class FoodSerializer(serializers.ModelSerializer):
    restoraunts = serializers.SerializerMethodField()
    
    class Meta:
        model = Food
        fields = [
            "slug",
            "genitive_case",
            "name",
            "title",
            "restoraunts"
        ]
        
    def get_restoraunts(self, food):
        return Restoraunt.objects.all()