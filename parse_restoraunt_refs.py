import asyncio
import os

import django

from parsing.parser import RestorauntFoodScrapper

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = RestorauntFoodScrapper()
asyncio.run(parser())
