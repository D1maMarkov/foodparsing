import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


def main():
    from food.models import Food

    genitive_cases = open("Исправленный список тегов").readlines()
    updated_foods = []
    foods = Food.objects.all()[::-1]

    for food, genitive_case in zip(foods, genitive_cases):
        food.genitive_case = genitive_case
        updated_foods.append(food)

    Food.objects.bulk_update(updated_foods, ['genitive_case'])

if __name__ == "__main__":
    main()
