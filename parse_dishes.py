from parsing.parser import RestorauntPageScrapper
import asyncio
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = RestorauntPageScrapper()
asyncio.run(parser())
