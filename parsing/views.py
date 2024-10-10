from parsing.parser import CityPageScrapper, CityScrapper, RestorauntFoodScrapper, RestorauntPageScrapper, RestorauntsParser
from django.http import HttpResponse


async def parse_cities_view(request):
    parser = CityScrapper()
    await parser()
    return HttpResponse(status=200)


async def parse_foods_view(request):
    parser = CityPageScrapper()
    await parser()
    return HttpResponse(status=200)


async def parse_restoraunts_view(request):
    parser = RestorauntsParser()
    await parser()

    return HttpResponse(status=200)


async def parse_dishes_view(request):
    restoraunt_page_scrapper = RestorauntPageScrapper()
    await restoraunt_page_scrapper()

    return HttpResponse(status=200)


async def parse_restoraunt_foods(request):           
    parser = RestorauntFoodScrapper()
    await parser()

    return HttpResponse(status=200)
