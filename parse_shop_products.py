import asyncio
import os

import django

from parsing.parser import ShopPageScrapper

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = ShopPageScrapper()
asyncio.run(parser())
