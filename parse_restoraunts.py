import asyncio
import os

import django

from parsing.parser import RestorauntsParser

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = RestorauntsParser()
asyncio.run(parser())
