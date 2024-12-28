import asyncio
import os

import django

from parsing.parser import ShopsParser

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = ShopsParser()
asyncio.run(parser())
