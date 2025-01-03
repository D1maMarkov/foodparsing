import asyncio
import os

import django

from parsing.parser import RestorauntFoodNewScrapper

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = RestorauntFoodNewScrapper()
asyncio.run(parser())