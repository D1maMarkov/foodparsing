import os
from urllib.parse import urlparse
import django
import asyncio
import aiohttp



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


async def download_image(session, url, save_dir):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                file_name = os.path.join(save_dir, os.path.basename(urlparse(url).path))
                with open(file_name, "wb") as file:
                    file.write(await response.read())    

    except Exception as e:
        print(e, "error")


async def download_all_images(image_urls, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    else:
        return

    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url, save_dir) for url in image_urls]
        await asyncio.gather(*tasks)
        
        
async def main():
    from food.models import Dish, Restoraunt
    
    async for restoraunt in Restoraunt.objects.all():
        dishes = Dish.objects.filter(restoraunt=restoraunt).exclude(image="/nofoto.png").values_list("image", flat=True)
        image_urls = []
        async for image in dishes:
            image_urls.append(image)
        await download_all_images(image_urls, os.path.join("static", str(restoraunt.id)))
        print(restoraunt.id)
asyncio.run(main())