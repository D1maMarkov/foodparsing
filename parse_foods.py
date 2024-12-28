import asyncio
import os

import django

from parsing.parser import CityPageScrapper

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = CityPageScrapper()
asyncio.run(parser())
