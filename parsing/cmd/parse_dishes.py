import asyncio
import os

import django

from parsing.parser import RestorauntPageScrapper

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = RestorauntPageScrapper()
asyncio.run(parser())
