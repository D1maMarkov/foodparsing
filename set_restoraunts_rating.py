import asyncio
import os
import random
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


async def main():
    from food.models import Restoraunt, Dish
    count = await Restoraunt.objects.acount()
    for i in range(0, count, 300):
        restoraunts = []
        async for restoraunt in Restoraunt.objects.all()[i:i+300]:
            dish_ids = Dish.objects.filter(restoraunt_id=restoraunt.id).values_list("id", flat=True)
            dish_id = random.choice(dish_ids)
            dish = Dish.objects.get(id=dish_id)
            restoraunt.image_link = f"/media/{dish.restoraunt_id}/{dish.image.split('/')[-1]}"
            restoraunts.append(restoraunt)
        
        await Restoraunt.objects.abulk_update(restoraunts, ["image_link"])

if __name__ == "__main__":
    asyncio.run(main())