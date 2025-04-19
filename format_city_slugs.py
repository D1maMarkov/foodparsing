import asyncio
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


async def main():
    from food.models import City
    count = await City.objects.acount()
    for i in range(0, count, 200):
        objs = []
        async for obj in City.objects.all()[i:i+200]:
            obj.slug = obj.slug.replace("_", "-").lower()
            objs.append(obj)

        await City.objects.abulk_update(objs, ["slug"])

if __name__ == "__main__":
    asyncio.run(main())