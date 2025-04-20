import asyncio
import os
from random import randint
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


async def main():
    from food.models import Restoraunt
    count = await Restoraunt.objects.acount()
    for i in range(0, count, 300):
        restoraunts = []
        print(i)
        async for restoraunt in Restoraunt.objects.all()[i:i+300]:
            restoraunt.rating = f"4.{randint(5, 9)}"
            restoraunts.append(restoraunt)
        
        await Restoraunt.objects.abulk_update(restoraunts, ["rating"])

if __name__ == "__main__":
    asyncio.run(main())