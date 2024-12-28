import asyncio
import os

import django

from parsing.parser import CityScrapper

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = CityScrapper()
asyncio.run(parser())
