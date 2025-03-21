import asyncio
import os
from random import randint
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


async def main():
    from food.models import CityShop
    count = await CityShop.objects.acount()
    for i in range(0, count, 300):
        shops = []
        async for shop in CityShop.objects.all()[i:i+300]:
            shop.rating = f"4.{randint(5, 9)}"
            shops.append(shop)
        
        await CityShop.objects.abulk_update(shops, ["rating"])

if __name__ == "__main__":
    asyncio.run(main())