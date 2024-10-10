import random
from bs4 import BeautifulSoup

from food.models import City, CityFood, Dish, DishCategory, Food, Restoraunt, RestorauntFood
from asyncio import Semaphore
import aiohttp
from asgiref.sync import sync_to_async
import asyncio
from django.conf import settings

from parsing.db import get_cities, get_restoraunts
from parsing.models import Proxy


class WebScrapper:
    def __init__(self, maximum_connections: int = 10):
        self.semaphore: Semaphore = Semaphore(maximum_connections)
        self.url = settings.PARSE_URL
        self.headers = {'User-Agent': 'MyApp/1.0', 'Accept': 'application/json'}
    
    @sync_to_async
    def get_proxies(self) -> list[str]:
        return [
            str(proxy) for proxy in Proxy.objects.all()
        ]


class RestorauntPageScrapper(WebScrapper):
    def __init__(self, maximum_connections: int = 10):
        super().__init__(maximum_connections)
        self.dish_models: list[Dish] = []
        
    async def parse_restoraunt_page(self, session: aiohttp.ClientSession, url: str, restoraunt_id: int, ind, slug: str, proxy: str=None) -> None:
        try:
            async with self.semaphore:
                response = await session.get(url, headers=self.headers, proxy=proxy)
                print(response.status, proxy)

                if response.status == 404:
                    await Restoraunt.objects.filter(slug=slug).adelete()

                if response.status == 200:
                    page_content = await response.read()

                    soup = BeautifulSoup(page_content, 'html.parser')

                    dishes = soup.find('ul', class_='c-list-cards')

                    if dishes:
                        for dish in dishes:
                            for elem in dish:
                                if not isinstance(elem, str):
                                    product = elem

                                    if product.find('h4'):
                                        product_name = product.find('h4').text
                                        product_image = product.find('div', class_='c-list-cards__img')
                                        product_image = product_image.get('style')

                                        product_image = product_image.replace("background-image: url('", '')
                                        product_image = product_image.replace("');", '')

                                        product_slug = product.find('a', class_='c-list-cards__link')
                                        product_slug = product.get('href')

                                        product_slug = product_slug.replace('menu/', '')
                                        product_slug = product_slug.replace('/', '')

                                        self.dish_models.append(
                                            Dish(
                                                name=product_name,
                                                restoraunt_id=restoraunt_id,
                                                slug=product_slug,
                                                image=product_image,
                                                category=dish_category
                                            )
                                        )
                                else:
                                    if len(elem) > 1:
                                        dish_category = await DishCategory.objects.filter(name=str(elem)).aexists()
                                        if not dish_category:
                                            dish_category = await DishCategory.objects.acreate(
                                                name=str(elem)
                                            )
                                        else:
                                            dish_category = await DishCategory.objects.aget(name=str(elem))

                    owner = soup.findAll('p', class_="l-article__h-text")
                    if owner:
                        owner = owner[-1].text
                        schedule = ""

                        if "Режим работы" in owner:
                            ind = owner.index("Режим работы")

                            owner, schedule = owner[0:ind], owner[ind::]

                        await Restoraunt.objects.filter(id=restoraunt_id).aupdate(
                            owner=owner,
                            schedule=schedule
                        )
        except Exception as e:
            print(e)


    async def __call__(self):
        proxies = await self.get_proxies()
        restoraunts = await get_restoraunts()

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(restoraunts), 100):
                reqs = []
                l = len(restoraunts)

                for k in range(i, min(i + 100, l)):
                    restoraunt = restoraunts.pop(0)
                    current_link = f'{self.url}/{restoraunt[0]}/place/{restoraunt[1]}/'
                    reqs.append(self.parse_restoraunt_page(session, current_link, restoraunt[2], k, restoraunt[1], random.choice(proxies)))

                await asyncio.gather(*reqs)
                reqs.clear()
                await Dish.objects.abulk_create(self.dish_models)
                self.dish_models.clear()


class CityPageScrapper(WebScrapper):
    def __init__(self, maximum_connections: int = 10):
        super().__init__(maximum_connections)
        self.food_models = []

    async def parse_city_page(self, session, url, ind, city_slug, city_id, proxy) -> None:
        try:
            async with self.semaphore:
                response = await session.get(url, headers=self.headers, proxy=proxy)
                print(response.status, proxy)
                print(ind)
                if response.status == 200:
                    page_content = await response.read()
                    soup = BeautifulSoup(page_content, 'html.parser')

                    foods = soup.findAll('a', class_='l-article__btn l-article__btn--small')

                    for food in foods:
                        name = food.text

                        slug = food.get('href')
                        slug = slug.replace('/', '')
                        slug = slug.replace(city_slug, '')

                        if not Food.objects.filter(name=name).exists():
                            food_obj = Food(
                                    name=name, slug=slug
                                )
                            food_obj.save()

                        CityFood.objects.update_or_create(
                            food=food_obj, city_id=city_id
                        )

        except Exception as e:
            print(e)


    async def __call__(self):
        cities = await get_cities()
        proxies = await self.get_proxies()

        async with aiohttp.ClientSession() as session:
            reqs = []
            for ind, city in enumerate(cities):
                city_slug = city.slug

                url = f'{self.url}/{city_slug}/'

                reqs.append(
                    self.parse_city_page(session, url, ind, city_slug, city.id, proxy = random.choice(proxies))
                )
            
            await asyncio.gather(*reqs)
            reqs.clear()


class RestorauntsParser(WebScrapper):
    def __init__(self, maximum_connections: int = 10):
        super().__init__(maximum_connections)
        self.restoraunts_to_update = []
        self.restoraunts_to_create = []
    
    async def parse_city_page(self, session, ind, city_slug, city_id):
        proxies = await self.get_proxies()

        print(ind)
        pageNum = 1
        while True:
            try:
                async with self.semaphore:
                    url = f'{self.url}/{city_slug}/page-{pageNum}'
                    response = await session.get(url, headers=self.headers, proxy=random.choice(proxies))
                    print(response.status)
                    if response.status == 200:
                        page_content = await response.read()
                        soup = BeautifulSoup(page_content, 'html.parser')

                        restoraunts = soup.find('ul', class_='c-list-cards')
                        restoraunts = restoraunts.findAll('a', class_='c-list-cards__link')
                        
                        if len(restoraunts) == 0:
                            break

                        for restoraunt in restoraunts:
                            name = restoraunt.find('div', class_='c-list-cards__header').text

                            slug = restoraunt.get('href')
                            slug = slug.replace('/', '')
                            slug = slug.replace('place', '')

                            image = restoraunt.find('div', 'c-list-cards__img')
                            image = image.get('style')

                            image = image.replace("background-image: url('", '')
                            image = image.replace("');", '')

                            if "https://" not in image:
                                image = f"{self.url}/{image}"

                        restoraunt_model = await Restoraunt.objects.filter(name=name, city_id=city_id).afirst()
                        if restoraunt_model:
                            if restoraunt_model.slug != slug or restoraunt_model.image != image:
                                restoraunt_model.slug = slug
                                restoraunt_model.image = image
                                self.restoraunts_to_update.append(restoraunt_model)
                        
                        else:
                            self.restoraunts_to_create.append(
                                Restoraunt(
                                    name=name, city_id=city_id, slug=slug, image=image
                                )
                            )

                        pageNum += 1

            except Exception as e:
                print(e)

    async def __call__(self):
        cities = await get_cities()
        
        async with aiohttp.ClientSession() as session:
            reqs = []
            for ind, city in enumerate(cities):
                reqs.append(self.parse_city_page(session, ind, city.slug, city.id))

            await asyncio.gather(*reqs)
            print(self.restoraunts_to_update)
            await Restoraunt.objects.abulk_update(self.restoraunts_to_update, ["slug", "image"])
            print(self.restoraunts_to_create)
            await Restoraunt.objects.abulk_create(self.restoraunts_to_create)
            reqs.clear()


class CityScrapper(WebScrapper):
    async def __call__(self):
        proxies = await self.get_proxies()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with self.semaphore:
                    response = await session.get(self.url, headers=self.headers, proxy=random.choice(proxies))
                    print(response.status)
                    if response.status == 200:
                        page_content = await response.read()
                        soup = BeautifulSoup(page_content, 'html.parser')
                        
                        cities = soup.findAll('a', class_='c-list__link')
                        for city in cities:
                            slug = city.get('href')
                            slug = slug.replace('/', '')

                            title = city.get('title')

                            name = city.find('div').text

                            City.objects.update_or_create(
                                name=name, defaults={"slug": slug, "title": title}
                            )

            except Exception as e:
                print(e)
                

class RestorauntFoodScrapper(WebScrapper):
    async def parse_restoraunt_page(self, session, city_slug, restoraunt_slug, restoraunt_id, ind):
        proxies = await self.get_proxies()
        
        url = f'{self.url}/{city_slug}/place/{restoraunt_slug}/'
        try:
            async with self.semaphore:
                response = await session.get(url, headers=self.headers, proxy=random.choice(proxies))
                
                print(response.status)
                print(ind)
                
                if response.status == 200:
                    page_content = await response.read()

                    soup = BeautifulSoup(page_content, 'html.parser')

                    try:
                        foods_container = soup.findAll('div', class_='white-box')[2]
                        foods = foods_container.findAll('p', class_='l-article__h-text')[2]
                        foods = foods.findAll('a', class_='l-article__btn')
                    except:
                        return

                    for food in foods:
                        slug = food.get('href')
                        slug = slug.replace(city_slug, '')
                        slug = slug.replace('/', '')

                        food_obj, _ = await Food.objects.aget_or_create(
                            name=food.text,
                            slug=slug
                        )

                        await RestorauntFood.objects.aupdate_or_create(
                            restoraunt_id=restoraunt_id,
                            food=food_obj
                        )
        except Exception as e:
                print(e)

    async def __call__(self):
        restoraunts = await get_restoraunts()
        
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(restoraunts), 100):
                reqs = []
                l = len(restoraunts)
                
                for k in range(i, min(i + 100, l)):
                    restoraunt = restoraunts.pop(0)
                    city_slug, slug, id = restoraunt
                    reqs.append(self.parse_restoraunt_page(session, city_slug, slug, id, k))
                
                await asyncio.gather(*reqs)
                reqs.clear()
