import asyncio
import os

import django

from parsing.parser import DishRefsGenerator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


parser = DishRefsGenerator()
asyncio.run(parser())
