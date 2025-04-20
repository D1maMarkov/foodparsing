import asyncio
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


async def main():
    from food.models import Restoraunt, Dish
    c = await Restoraunt.objects.acount()

    for i in range(0, c, 200):
        restoraunts = []
        print(i)
        async for r in Restoraunt.objects.all()[i:i+200]:
            d = await Dish.objects.filter(restoraunt_id=r.id).aexists()
            r.have_dishes = d
            restoraunts.append(r)

        await Restoraunt.objects.abulk_update(restoraunts, fields=["have_dishes"])

if __name__ == "__main__":
    asyncio.run(main())
