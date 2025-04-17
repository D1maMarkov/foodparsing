import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


def main():
    from food.models import CityShop

    all_shops = list(CityShop.objects.all().values_list("slug", "city__name"))
    #print(all_shops)
    print("start")
    for shop in set(all_shops):
        if all_shops.count(shop) > 1:
            print(shop)


if __name__ == "__main__":
    main()
