import os
import django
import asyncio

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


async def main():
    from food.models import RestorauntRef

    await RestorauntRef.objects.aupdate(text="")


if __name__ == "__main__":
    asyncio.run(main())