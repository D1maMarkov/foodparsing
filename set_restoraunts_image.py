import asyncio
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


async def main():
    from food.models import Restoraunt, Dish
    count = await Restoraunt.objects.acount()
    for i in range(0, count, 300):
        restoraunts = []
        async for restoraunt in Restoraunt.objects.all()[i:i+300]:
            #print(restoraunt.image_link, os.path.exists("/home/static" + restoraunt.image_link[restoraunt.image_link.find("/", 1)::]))
            if not restoraunt.image_link:
                continue
            if not os.path.exists("/home/static" + restoraunt.image_link[restoraunt.image_link.find("/", 1)::]):
                restoraunt.image_link = None
                restoraunts.append(restoraunt)
                #continue

            '''if restoraunt.image_link:
                continue
            dish_ids = []
            async for d in Dish.objects.filter(restoraunt_id=restoraunt.id).values_list("id", flat=True):
                dish_ids.append(d)
            if not dish_ids:
                continue
            dish_id = random.choice(dish_ids)
            dish = await Dish.objects.aget(id=dish_id)
            restoraunt.image_link = f"/media/{dish.restoraunt_id}/{dish.image.split('/')[-1]}"
            restoraunts.append(restoraunt)'''

        await Restoraunt.objects.abulk_update(restoraunts, ["image_link"])

async def main():
    from food.models import Restoraunt, Dish
    m = 0
    async for r in Restoraunt.objects.values_list("image_link", flat=True):
        m = max(m, len(r))
    print(m)


async def main():
    from food.models import Restoraunt
    count = await Restoraunt.objects.acount()
    for i in range(0, count, 300):
        restoraunts = []
        async for restoraunt in Restoraunt.objects.all()[i:i+300]:
            if not restoraunt.image_link:
                continue
            restoraunt.image_link = restoraunt.image_link.replace("/media/", "")
            restoraunts.append(restoraunt)

        await Restoraunt.objects.abulk_update(restoraunts, ["image_link"])

if __name__ == "__main__":
    asyncio.run(main())
