import asyncio
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


def main():
    from parsing.parser import ShopPageScrapper
    
    parser = ShopPageScrapper()
    asyncio.run(parser())
    

if __name__ == "__main__":
    main()
