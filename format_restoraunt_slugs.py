import asyncio
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


async def main():
    from food.models import Restoraunt
    count = await Restoraunt.objects.acount()
    for i in range(0, count, 200):
        restoraunts = []
        async for restoraunt in Restoraunt.objects.all()[i:i+200]:
            if "_" in restoraunt.slug:
                restoraunt.slug = restoraunt.slug.replace("_", "-")
                restoraunts.append(restoraunt)
        
        await Restoraunt.objects.abulk_update(restoraunts, ["slug"])

if __name__ == "__main__":
    asyncio.run(main())