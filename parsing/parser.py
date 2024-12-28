import asyncio
import random
from asyncio import Semaphore

import aiohttp
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import Count

from food.models import (
    City,
    CityFood,
    CityShop,
    Dish,
    DishCategory,
    DishRef,
    Food,
    Restoraunt,
    RestorauntFood,
    RestorauntRef,
    Shop,
    ShopCategory,
    ShopProduct,
)
from parsing.db import get_cities, get_city_shops, get_restoraunts
from parsing.models import Proxy


class WebScrapper:
    def __init__(self, maximum_connections: int = 10):
        self.semaphore: Semaphore = Semaphore(maximum_connections)
        self.url = settings.PARSE_URL
        self.headers = {"User-Agent": "MyApp/1.0", "Accept": "application/json"}

    @sync_to_async
    def get_proxies(self) -> list[str]:
        return [str(proxy) for proxy in Proxy.objects.all()]


class RestorauntPageScrapper(WebScrapper):
    def __init__(self, maximum_connections: int = 10):
        super().__init__(maximum_connections)
        self.dish_models: list[Dish] = []

    async def parse_restoraunt_page(
        self, session: aiohttp.ClientSession, url: str, restoraunt_id: int, ind, slug: str, proxy: str | None = None
    ) -> None:
        try:
            dish_category: DishCategory
            async with self.semaphore:
                response = await session.get(url, headers=self.headers, proxy=proxy)
                # print(response.status, ind)

                if response.status == 404:
                    await Restoraunt.objects.filter(slug=slug).adelete()

                if response.status == 200:
                    page_content = await response.read()

                    soup = BeautifulSoup(page_content, "html.parser")

                    dishes = soup.find("ul", class_="c-list-cards")

                    if dishes:
                        for dish in dishes:
                            for elem in dish:
                                if not isinstance(elem, str):
                                    product = elem

                                    if product.find("h4"):
                                        product_name = product.find("h4").text
                                        product_image = product.find("div", class_="c-list-cards__img")
                                        product_image = product_image.get("style")

                                        product_image = product_image.replace("background-image: url('", "")
                                        product_image = product_image.replace("');", "")

                                        product_slug = product.find("a", class_="c-list-cards__link")
                                        product_slug = product.get("href")

                                        product_slug = product_slug.replace("menu/", "")
                                        product_slug = product_slug.replace("/", "")

                                        product_price = product.find("b")
                                        if product_price:
                                            product_price = product_price.text.strip()

                                        product_weight = product.findAll("small")[-2]
                                        if product_weight:
                                            product_weight = product_weight.text.strip()[5::]

                                        self.dish_models.append(
                                            Dish(
                                                name=product_name,
                                                restoraunt_id=restoraunt_id,
                                                slug=product_slug,
                                                image=product_image,
                                                category=dish_category,
                                                price=product_price,
                                                weight=product_weight,
                                                unique_key=f"{restoraunt_id}/{product_slug}",
                                            )
                                        )

                                else:
                                    if len(elem) > 1:
                                        dish_category = await DishCategory.objects.filter(name=str(elem)).aexists()
                                        if not dish_category:
                                            dish_category = await DishCategory.objects.acreate(name=str(elem))
                                        else:
                                            dish_category = await DishCategory.objects.filter(name=str(elem)).afirst()

                    owner = soup.findAll("p", class_="l-article__h-text")
                    if owner:
                        owner = owner[-1].text
                        schedule = ""

                        if "Режим работы" in owner:
                            ind = owner.index("Режим работы")

                            owner, schedule = owner[0:ind], owner[ind::]

                        await Restoraunt.objects.filter(id=restoraunt_id).aupdate(owner=owner, schedule=schedule)
        except Exception as e:
            print(e)

    async def __call__(self):
        proxies = await self.get_proxies()
        restoraunts = await get_restoraunts()
        print(len(restoraunts))

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(restoraunts), 1):
                reqs = []
                len_resporaunts = len(restoraunts)

                for k in range(i, min(i + 1, i + len_resporaunts)):
                    restoraunt = restoraunts.pop(0)
                    current_link = f"{self.url}/{restoraunt[0]}/place/{restoraunt[1]}/"
                    reqs.append(
                        self.parse_restoraunt_page(
                            session, current_link, restoraunt[2], k, restoraunt[1], random.choice(proxies)
                        )
                    )

                await asyncio.gather(*reqs)
                reqs.clear()
                print("creating...")
                try:
                    await Dish.objects.abulk_create(
                        self.dish_models,
                        # update_conflicts=True,
                        # unique_fields=["unique_key"],
                        # update_fields=["name", "image", "price", "weight"]
                    )
                except Exception as e:
                    print(e)
                print("created")
                self.dish_models.clear()


class CityPageScrapper(WebScrapper):
    def __init__(self, maximum_connections: int = 10):
        super().__init__(maximum_connections)
        self.food_models: list[Food] = []

    async def parse_city_page(self, session, url, ind, city_slug, city_id, proxy) -> None:
        try:
            async with self.semaphore:
                response = await session.get(url, headers=self.headers, proxy=proxy)
                print(response.status, proxy)
                print(ind)
                if response.status == 200:
                    page_content = await response.read()
                    soup = BeautifulSoup(page_content, "html.parser")

                    foods = soup.findAll("a", class_="l-article__btn l-article__btn--small")

                    for food in foods:
                        name = food.text

                        slug = food.get("href")
                        slug = slug.replace("/", "")
                        slug = slug.replace(city_slug, "")
                        food_obj, created = await Food.objects.aget_or_create(name=name)
                        # if not exist:
                        # food_obj = await Food.objects.acreate(
                        #    name=name, slug=slug
                        # )

                        await CityFood.objects.acreate(food=food_obj, city_id=city_id)

        except Exception as e:
            print(e)

    async def __call__(self):
        cities = await get_cities()
        proxies = await self.get_proxies()

        async with aiohttp.ClientSession() as session:
            reqs = []
            for ind, city in enumerate(cities):
                city_slug = city.slug

                url = f"{self.url}/{city_slug}/"

                reqs.append(self.parse_city_page(session, url, ind, city_slug, city.id, proxy=random.choice(proxies)))

            await asyncio.gather(*reqs)
            reqs.clear()


class RestorauntsParser(WebScrapper):
    def __init__(self, maximum_connections: int = 10):
        super().__init__(maximum_connections)
        self.restoraunts_to_create: list[Restoraunt] = []

    async def create_restoraunts(self) -> None:
        await Restoraunt.objects.abulk_create(
            self.restoraunts_to_create,
            update_conflicts=True,
            unique_fields=["unique_key"],
            update_fields=["name", "city_id", "address", "slug", "image", "min_order", "price_category"],
            batch_size=300,
        )

        self.restoraunts_to_create.clear()

    async def parse_city_page(self, session, ind, city_slug, city_id, proxy):
        pageNum = 1
        print(ind)
        while True:
            if len(self.restoraunts_to_create) > 300:
                await self.create_restoraunts()

            try:
                async with self.semaphore:
                    url = f"{self.url}/{city_slug}/page-{pageNum}"
                    response = await session.get(url, headers=self.headers, proxy=proxy)
                    if response.status == 200:
                        page_content = await response.read()
                        soup = BeautifulSoup(page_content, "html.parser")

                        restoraunts = soup.find("ul", class_="c-list-cards")
                        restoraunts = restoraunts.findAll("a", class_="c-list-cards__link")

                        if len(restoraunts) == 0:
                            break

                        for restoraunt in restoraunts:
                            name = restoraunt.find("div", class_="c-list-cards__header").text

                            slug = restoraunt.get("href")
                            slug = slug.replace("/", "")
                            slug = slug.replace("place", "")

                            image = restoraunt.find("div", "c-list-cards__img")
                            image = image.get("style")

                            image = image.replace("background-image: url('", "")
                            image = image.replace("');", "")

                            if "https://" not in image:
                                image = f"{self.url}/{image}"

                            address = restoraunt.find("small").text

                            price_category = restoraunt.find("div", "price-range")
                            price_category = price_category.find("b").text

                            min_order = restoraunt.findAll("b")[-1].text

                            self.restoraunts_to_create.append(
                                Restoraunt(
                                    name=name,
                                    city_id=city_id,
                                    address=address,
                                    slug=slug,
                                    image=image,
                                    min_order=min_order,
                                    price_category=price_category,
                                    unique_key=f"{city_id}/{slug}",
                                )
                            )

                        pageNum += 1

            except Exception as e:
                print(e)

        print(ind, "finished")

    async def __call__(self):
        proxies = await self.get_proxies()
        cities = await get_cities()

        async with aiohttp.ClientSession() as session:
            reqs = []
            for ind, city in enumerate(cities):
                reqs.append(self.parse_city_page(session, ind, city.slug, city.id, proxy=random.choice(proxies)))

            await asyncio.gather(*reqs)
            await self.create_restoraunts()
            reqs.clear()


class CityScrapper(WebScrapper):
    async def __call__(self):
        # proxies = await self.get_proxies()
        proxies = []
        if proxies:
            proxy = random.choice(proxies)
        else:
            proxy = None

        async with aiohttp.ClientSession() as session:
            try:
                async with self.semaphore:
                    response = await session.get(self.url, headers=self.headers, proxy=proxy)
                    print(response.status)
                    if response.status == 200:
                        page_content = await response.read()
                        soup = BeautifulSoup(page_content, "html.parser")

                        cities = soup.findAll("a", class_="c-list__link")
                        for city in cities:
                            slug = city.get("href")
                            slug = slug.replace("/", "")

                            title = city.get("title")

                            name = city.find("div").text

                            await City.objects.aupdate_or_create(name=name, defaults={"slug": slug, "title": title})

            except Exception as e:
                print(e)


class RestorauntFoodScrapper(WebScrapper):
    foods: dict[str, Food] = {}
    res_foods: list[RestorauntFood] = []

    async def parse_restoraunt_page(self, session, city_slug, restoraunt_slug, restoraunt_id, ind, proxy):
        url = f"{self.url}/{city_slug}/place/{restoraunt_slug}/"
        try:
            # if 2:
            async with self.semaphore:
                response = await session.get(url, headers=self.headers, proxy=proxy)

                print(response.status)
                print(ind)

                if response.status == 200:
                    page_content = await response.read()

                    soup = BeautifulSoup(page_content, "html.parser")

                    try:
                        foods_container = soup.findAll("div", class_="white-box")[2]
                        foods = foods_container.findAll("p", class_="l-article__h-text")[2]
                        foods = foods.findAll("a", class_="l-article__btn")
                    except:
                        # print("returned")
                        return

                    # print(foods, restoraunt_slug, city_slug)

                    for food in foods:
                        slug = food.get("href")
                        slug = slug.replace(city_slug, "")
                        slug = slug.replace("/", "")

                        if food.text not in self.foods.keys():
                            food_obj = await Food.objects.acreate(
                                name=food.text,
                            )

                            self.foods[food.text] = food_obj
                        else:
                            food_obj = self.foods[food.text]

                        # print(food_obj)

                        self.res_foods.append(RestorauntFood(restoraunt_id=restoraunt_id, food=food_obj))
        except Exception as e:
            print(e)

    async def __call__(self):
        proxies = await self.get_proxies()
        restoraunts = await get_restoraunts()
        print(len(restoraunts))

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(restoraunts), 100):
                reqs = []
                len_resporaunts = len(restoraunts)

                for k in range(i, min(i + 100, i + len_resporaunts)):
                    restoraunt = restoraunts.pop(0)
                    city_slug, slug, id = restoraunt
                    reqs.append(
                        self.parse_restoraunt_page(session, city_slug, slug, id, k, proxy=random.choice(proxies))
                    )

                await asyncio.gather(*reqs)
                print("creating...")
                print(len(self.res_foods))
                await RestorauntFood.objects.abulk_create(self.res_foods, batch_size=150)
                print("created")
                self.res_foods.clear()
                # await RestorauntRef.objects.abulk_create(
                #    self.refs_to_create,
                #    batch_size=150
                # update_conflicts=True,
                # unique_fields=["unique_key"],
                # update_fields=["restoraunt_id", "ref"]
                # )
                # self.refs_to_create.clear()
                reqs.clear()

        #        await RestorauntRef.objects.abulk_create(self.refs_to_create)
        self.refs_to_create.clear()


class RestorauntRefsScrapper(WebScrapper):
    refs_to_create: list[RestorauntRef] = []

    async def parse_restoraunt_page(self, session, city_slug, restoraunt_slug, restoraunt_id, ind, proxy):
        url = f"{self.url}/{city_slug}/place/{restoraunt_slug}/"
        try:
            async with self.semaphore:
                response = await session.get(url, headers=self.headers, proxy=proxy)

                print(response.status)
                print(ind)

                if response.status == 200:
                    page_content = await response.read()

                    soup = BeautifulSoup(page_content, "html.parser")

                    a_tags = soup.findAll("a")
                    ref_buttons = []
                    for a in a_tags:
                        if a.get("target") == "_blank":
                            if "go.php" in a.get("href"):
                                # print(111)
                                # print(a.get("href"), a.text)
                                # print(111)
                                ref_buttons.append(a.get("href"))

                    # print(ref_buttons)
                    refs = set()
                    for ref in ref_buttons:
                        async with aiohttp.ClientSession() as session:
                            response = await session.get(f"{self.url}/{ref}")
                            s = await response.read()
                            s = str(s)
                            # print(response.status)
                            start = s.find("ulp=") + len("ulp=")
                            end = s.rfind("redirect()")

                            if start != -1 and end != -1:
                                s = s[start:end]
                                s = s.strip()
                                s = s.replace(r"\n", "")
                                s = s.strip(r"}")
                                s = s.strip()
                                s = s.strip(r";")
                                s = s.strip(r"'")
                                s = s.strip(r"'")
                                s = s[0:-1]
                                s = s.replace("%3A", ":")
                                s = s.replace("%2F", "/")
                            else:
                                pass  # print("Подстрока не найдена.")

                            # print(s)
                            if "market-delivery.yandex.ru" in s:
                                if "/r/" in s:
                                    refs.add(s)
                            elif "eda.yandex.ru" in s:
                                if "restaurant" in s:
                                    refs.add(s)
                            else:
                                refs.add(s)

                    refs = list(refs)
                    for ref in refs:
                        self.refs_to_create.append(
                            RestorauntRef(ref=ref, restoraunt_id=restoraunt_id, unique_key=f"{restoraunt_id}/{ref}")
                        )
        except Exception as e:
            print(e)

    async def __call__(self):
        proxies = await self.get_proxies()
        restoraunts = await get_restoraunts()
        print(len(restoraunts))

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(restoraunts), 100):
                reqs = []
                len_resporaunts = len(restoraunts)

                for k in range(i, min(i + 100, i + len_resporaunts)):
                    restoraunt = restoraunts.pop(0)
                    city_slug, slug, id = restoraunt
                    reqs.append(
                        self.parse_restoraunt_page(session, city_slug, slug, id, k, proxy=random.choice(proxies))
                    )

                await asyncio.gather(*reqs)
                print("creating...")
                print(len(self.res_foods))
                await RestorauntFood.objects.abulk_create(self.res_foods, batch_size=150)
                print("created")
                self.res_foods.clear()
                # await RestorauntRef.objects.abulk_create(
                #    self.refs_to_create,
                #    batch_size=150
                # update_conflicts=True,
                # unique_fields=["unique_key"],
                # update_fields=["restoraunt_id", "ref"]
                # )
                # self.refs_to_create.clear()
                reqs.clear()

        #        await RestorauntRef.objects.abulk_create(self.refs_to_create)
        self.refs_to_create.clear()


@sync_to_async
def get_restoraunt_refs(restoraunt_id):
    return list(RestorauntRef.objects.filter(restoraunt_id=restoraunt_id).values_list("ref", flat=True))


class DishRefsGenerator:
    async def __call__(self):
        print(11111)

        refs = []
        res_ids = Restoraunt.objects.values_list("id", flat=True).all()
        async for restoraunt_id in res_ids:
            async for dish in Dish.objects.filter(restoraunt_id=restoraunt_id).annotate(count=Count("refs")).filter(
                count=0
            ):
                dish_refs = await self.generate_dish_refs(dish)
                refs.extend(dish_refs)
            print(restoraunt_id)

            if len(refs) > 300:
                await DishRef.objects.abulk_create(
                    refs,
                    # update_conflicts=True,
                    # unique_fields=["unique_key"],
                    # update_fields=["dish_id", "ref"]
                )
                # print(i)
                refs.clear()
        await DishRef.objects.abulk_create(
            refs,
            # update_conflicts=True,
            # unique_fields=["unique_key"],
            # update_fields=["dish_id", "ref"]
        )
        # print(i)
        refs.clear()

        print(333)

    async def generate_dish_refs(self, dish):
        restoraunt_refs = await get_restoraunt_refs(dish.restoraunt_id)

        refs = []

        for restoraunt_ref in restoraunt_refs:
            dish_ref = f"{restoraunt_ref}?search={dish.name}"
            refs.append(DishRef(ref=dish_ref, dish_id=dish.id, unique_key=f"{dish.id}/{dish_ref}"))

        return refs


class ShopsParser(WebScrapper):
    def __init__(self, maximum_connections: int = 10):
        super().__init__(maximum_connections)
        self.shops: list[CityShop] = []

    async def parse_city_page(self, session, ind, city_slug, city_id, proxies):
        try:
            async with self.semaphore:
                url = f"{self.url}/{city_slug}/"
                response = await session.get(url, headers=self.headers, proxy=random.choice(proxies))
                print(ind)
                print(response.status)
                if response.status == 200:
                    page_content = await response.read()
                    soup = BeautifulSoup(page_content, "html.parser")

                    shops = soup.findAll("section", class_="l-article__section")[-1]
                    shops = shops.find("ul", class_="c-list-cards")
                    shops = shops.findAll("a", class_="c-list-cards__link")

                    if len(shops) == 0:
                        return

                    for shop in shops:
                        shop_name = shop.find("div", class_="c-list-cards__header").text

                        slug = shop.get("href")
                        slug = slug.replace("/", "")
                        slug = slug.replace("place-market", "")

                        image = shop.find("div", "c-list-cards__img")
                        image = image.get("style")

                        image = image.replace("background-image: url('", "")
                        image = image.replace("');", "")

                        if "https://" not in image:
                            image = f"{self.url}/{image}"
                            image = image.replace("//", "/")

                        address = shop.find("small").text
                        # print(address)

                        price_category = shop.find("div", "price-range")
                        price_category = price_category.find("b").text
                        # print(price_category)

                        min_order = shop.findAll("b")[-1].text
                        # print(min_order)

                        """restoraunt_model = await Restoraunt.objects.filter(slug=slug, city_id=city_id).afirst()
                        if restoraunt_model:
                            #if restoraunt_model.slug != slug or restoraunt_model.image != image or restoraunt_model.address != address or restoraunt_model.price_category != price_category or restoraunt_model.min_order != min_order:
                                restoraunt_model.name = name
                                restoraunt_model.image = image
                                restoraunt_model.min_order = min_order
                                restoraunt_model.price_category = price_category
                                restoraunt_model.address = address
                                self.restoraunts_to_update.append(restoraunt_model)

                        else:
                            self.restoraunts_to_create.append(
                                Restoraunt(
                                    name=name, city_id=city_id, address=address, slug=slug, image=image, min_order=min_order, price_category=price_category
                                )
                            )"""
                        # print(shop_name)
                        # print(slug)
                        # print(image)
                        # print(address)
                        # print(price_category)

                        """shop_model = None
                        for shop_obj in shops_models:
                            if shop_obj.name == shop_name:
                                shop_model = shop_obj
                                break

                        if shop_model is None:
                            shop_model = await Shop.objects.acreate(
                                name=shop_name,
                                image=image,
                                address=address,
                                min_order=min_order,
                                price_category=price_category
                            )

                            shops_models.append(shop_model)"""

                        shop_model, _ = await Shop.objects.aget_or_create(
                            name=shop_name,
                            defaults={
                                "image": image,
                                "address": address,
                                "min_order": min_order,
                                "price_category": price_category,
                            },
                        )

                        self.shops.append(
                            CityShop(
                                # unique_key=f"{city_id}/{shop_model.name}",
                                slug=slug,
                                city_id=city_id,
                                shop_id=shop_model.id,
                            )
                        )

        except Exception as e:
            print(e)

    async def __call__(self):
        cities = await get_cities()
        proxies = await self.get_proxies()

        async with aiohttp.ClientSession() as session:
            reqs = []
            for ind, city in enumerate(cities):
                reqs.append(self.parse_city_page(session, ind, city.slug, city.id, proxies))

            await asyncio.gather(*reqs)

            # try:
            await CityShop.objects.abulk_create(
                self.shops,
                batch_size=1000
                # update_conflicts=True,
                # unique_fields=["unique_key"],
                # update_fields=["city_id", "slug", "shop_id"]
            )
            # except:
            #    print("something went wrong while creating")

            self.shops.clear()
            reqs.clear()


class ShopPageScrapper(WebScrapper):
    def __init__(self, maximum_connections: int = 100) -> None:
        super().__init__(maximum_connections)
        self.product_models: list[Dish] = []

    async def parse_shop_page(
        self, session: aiohttp.ClientSession, url: str, shop_id: int, ind, proxy: str | None = None
    ) -> None:
        try:
            product_category: ShopCategory
            async with self.semaphore:
                response = await session.get(url, headers=self.headers, proxy=proxy)
                print(response.status, ind)

                if response.status == 200:
                    page_content = await response.read()

                    soup = BeautifulSoup(page_content, "html.parser")

                    products = soup.find("ul", class_="c-list-cards")

                    if products:
                        for product_html in products:
                            for elem in product_html:
                                if not isinstance(elem, str):
                                    product = elem

                                    if product.find("h4"):
                                        product_name = product.find("h4").text
                                        product_image = product.find("div", class_="c-list-cards__img")
                                        product_image = product_image.get("style")

                                        product_image = product_image.replace("background-image: url('", "")
                                        product_image = product_image.replace("');", "")

                                        product_slug = product.find("a", class_="c-list-cards__link")
                                        product_slug = product.get("href")

                                        product_slug = product_slug.replace("catalog/", "")
                                        product_slug = product_slug.replace("/", "")

                                        product_price = product.find("b")
                                        if product_price:
                                            product_price = product_price.text.strip()

                                        product_weight = product.findAll("small")[-1]
                                        if product_weight:
                                            product_weight = product_weight.text.strip()[5::]

                                        self.product_models.append(
                                            ShopProduct(
                                                name=product_name,
                                                shop_id=shop_id,
                                                slug=product_slug,
                                                image=product_image,
                                                category=product_category,
                                                price=product_price,
                                                weight=product_weight,
                                                unique_key=f"{shop_id}/{product_slug}",
                                            )
                                        )

                                    else:
                                        try:
                                            if "l-article__h2" in product["class"]:
                                                # print(product.text)
                                                name = product.text
                                                # print()
                                                product_category, _ = await ShopCategory.objects.aget_or_create(
                                                    name=name
                                                )
                                        except:
                                            pass

                    # owner = soup.findAll("p", class_="l-article__h-text")
                    # if owner:
                    #    owner = owner[-1].text
                    #    schedule = ""

                    #    if "Режим работы" in owner:
                    #        ind = owner.index("Режим работы")

                    #        owner, schedule = owner[0:ind], owner[ind::]

                    #    """await Shop.objects.filter(id=shop_id).aupdate(
                    #        owner=owner,
                    #        schedule=schedule
                    #    )"""
        except Exception as e:
            print(e, "123")

    async def __call__(self):
        proxies = await self.get_proxies()
        shops = await get_city_shops()
        print(len(shops))

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(shops), 100):
                reqs = []
                len_shops = len(shops)

                for k in range(i, min(i + 100, i + len_shops)):
                    shop = shops.pop(0)
                    current_link = f'{self.url}/{shop["city__slug"]}/place-market/{shop["slug"]}/'
                    reqs.append(self.parse_shop_page(session, current_link, shop["id"], k, random.choice(proxies)))

                await asyncio.gather(*reqs)
                reqs.clear()
                print("creating...")
                # try:
                await ShopProduct.objects.abulk_create(
                    self.product_models,
                    # update_conflicts=True,
                    # unique_fields=["unique_key"],
                    # update_fields=["name", "image", "slug", "category", "price", "weight"]
                )
                # except:
                #    print("something went wrong while creating")
                print("created")
                self.product_models.clear()
