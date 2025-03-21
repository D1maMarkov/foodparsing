import random

from ckeditor.fields import RichTextField
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name="город")
    title = models.CharField(max_length=200, null=True)
    slug = models.CharField(max_length=100, null=True)

    genitive_case = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.genitive_case:
            self.genitive_case = self.title.split()[-1]

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        
    @property
    def dslug(self):
        return self.slug.replace("_", "-")


class Food(models.Model):
    name = models.CharField(max_length=100, verbose_name="кухня")
    slug = models.CharField(max_length=100, null=True)
    genitive_case = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Кухня"
        verbose_name_plural = "Кухни"
        
    @property
    def dslug(self):
        return self.slug.replace("_", "-")


class Restoraunt(models.Model):
    name = models.CharField(max_length=150, verbose_name="Ресторан")
    slug = models.CharField(max_length=150, null=True)
    city = models.ForeignKey(
        City, verbose_name="Город", on_delete=models.CASCADE, related_name="restoraunts"
    )

    image = models.CharField(null=True, verbose_name="Картинка", max_length=2000)
    owner = models.TextField(max_length=7000, null=True, verbose_name="Владелец")
    schedule = models.CharField(max_length=300, null=True, verbose_name="Расписание")
    address = models.CharField(max_length=500, null=True, verbose_name="Адрес")
    price_category = models.CharField(null=True, max_length=20, verbose_name="Ценовая категория")
    min_order = models.CharField(null=True, max_length=20, verbose_name="Минимальный заказ")
    unique_key = models.CharField(null=True, max_length=100, unique=True, blank=True)
    rating = models.CharField(null=True, max_length=3, verbose_name="Рейтинг")

    def __str__(self) -> str:
        return self.name

    @property
    def dslug(self):
        return self.slug.replace("_", "-")
    
    @property
    def image_link(self) -> str:
        dish_ids = Dish.objects.filter(restoraunt_id=self.id).values_list("id", flat=True)
        dish_id = random.choice(dish_ids)
        dish = Dish.objects.get(id=dish_id)
        return dish.image_link
    
    @property
    def dish_categories_count(self) -> int:
        return DishCategory.objects.filter(dishes__restoraunt_id=self.id).distinct().count()

    @property
    def dish_categories_html(self) -> str:
        categories = DishCategory.objects.filter(dishes__restoraunt_id=self.id).distinct().values_list("name", flat=True)
        html = ''
        
        for category in categories:
            html += f'''&bull; &nbsp;<span style="cursor: pointer;" onclick="selectFoodCategory(this)" >{category}</span><br />'''

        return html
    
    @property
    def full_address(self) -> str:
        if self.address.startswith(self.city.name):
            return self.address
        
        return f'''{self.city.name}, {self.address}'''

    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"


class Ref(models.Model):
    ref = models.URLField(verbose_name="ссылка", max_length=350)
    text = models.CharField(max_length=50, default="Заказать")

    def __str__(self):
        return self.text

    class Meta:
        abstract = True


class RestorauntRef(Ref):
    restoraunt = models.ForeignKey(Restoraunt, on_delete=models.CASCADE, related_name="refs")

    class Meta:
        verbose_name = "ссылка для ресторана"
        verbose_name_plural = "ссылки для ресторана"


class DishCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Категория блюд")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория блюда"
        verbose_name_plural = "Категории блюд"


class Dish(models.Model):
    name = models.CharField(max_length=200, verbose_name="Блюдо")
    restoraunt = models.ForeignKey(
        Restoraunt, on_delete=models.CASCADE, verbose_name="Заведение", related_name="dishes"
    )
    image = models.URLField(max_length=1000, verbose_name="Изображение", null=True)
    slug = models.CharField(max_length=300)
    category = models.ForeignKey(
        DishCategory, verbose_name="категория", on_delete=models.CASCADE, null=True, related_name="dishes"
    )
    price = models.CharField(max_length=10, verbose_name="Цена", null=True)
    weight = models.CharField(max_length=15, verbose_name="Вес", null=True, blank=True)
    unique_key = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.name
    
    @property
    def dslug(self):
        return self.slug.replace("_", "-")
    
    @property
    def image_link(self):
        return f"/media/{self.restoraunt_id}/{self.image.split('/')[-1]}"

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"


class DishRef(Ref):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="refs")

    class Meta:
        verbose_name = "ссылка для блюда"
        verbose_name_plural = "ссылки для блюда"


class RestorauntFood(models.Model):
    restoraunt = models.ForeignKey(Restoraunt, on_delete=models.CASCADE, related_name="foods")
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="restoraunt_foods")


class Seo(models.Model):
    PAGE_TYPES = [
        ("Главная", "Главная"),
        ("Город", "Город"),
        ("Ресторан", "Ресторан"),
        ("Магазин", "Магазин"),
        ("Кухня", "Кухня"),
    ]
    page_type = models.CharField(max_length=100, choices=PAGE_TYPES, verbose_name="страница")
    title = models.CharField(max_length=300)
    h1 = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(max_length=3000)

    text = RichTextField(max_length=7000, null=True, blank=True)

    class Meta:
        verbose_name = "Seo"
        verbose_name_plural = "Seo"

    def __str__(self):
        return self.page_type


class Shop(models.Model):
    name = models.CharField(verbose_name="Магазин", max_length=50)
    image = models.URLField(verbose_name="Изображение", max_length=200)
    address = models.CharField(verbose_name="Адрес", max_length=100)

    min_order = models.CharField(verbose_name="Минимальный заказ", max_length=10)
    price_category = models.CharField(verbose_name="Ценовая категория", max_length=10)

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"

    def __str__(self):
        return self.name


class CityShop(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="city_shops")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="shops")
    slug = models.CharField(max_length=90)
    unique_key = models.CharField(max_length=30, unique=True, null=True)
    rating = models.CharField(max_length=3, null=True)
    
    @property
    def dslug(self):
        return self.slug.replace("_", "-")

    class Meta:
        verbose_name = "Магазин в городе"
        verbose_name_plural = "Магазины в городах"

    def __str__(self) -> str:
        return f"{self.shop.name} {self.city.name}"
    
    @property
    def name(self) -> str:
        return self.shop.name
    
    @property
    def address(self) -> str:
        return self.shop.address


class ShopCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Категория товаров")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория товаров"
        verbose_name_plural = "Категории товаров"


class ShopProduct(models.Model):
    shop = models.ForeignKey(CityShop, on_delete=models.CASCADE, verbose_name="магазин", related_name="products")
    name = models.CharField(max_length=300, verbose_name="Товар")
    image = models.URLField(max_length=1000, verbose_name="Изображение", null=True)
    slug = models.CharField(max_length=50)
    category = models.ForeignKey(
        ShopCategory, verbose_name="категория", on_delete=models.CASCADE, null=True, related_name="products"
    )
    price = models.CharField(max_length=10, verbose_name="Цена", null=True)
    weight = models.CharField(max_length=15, verbose_name="Вес", null=True, blank=True)
    unique_key = models.CharField(max_length=40)
    
    
    @property
    def dslug(self):
        return self.slug.replace("_", "-")

    class Meta:
        verbose_name = "продукт в магазине"
        verbose_name_plural = "продукты в магазине"

    def __str__(self) -> str:
        return f"{self.shop.shop.name} {self.name}"


class Button(models.Model):
    ref = models.CharField(max_length=400, verbose_name="ссылка")
    text = models.CharField(max_length=50, verbose_name="текст", default="Заказать")

    BUTTON_TYPES = [
        ("Яндекс", "Яндекс"),
        ("Деливери", "Деливери"),
    ]
    
    type = models.CharField(max_length=10, verbose_name="сервис", choices=BUTTON_TYPES, default="Яндекс")
    
    class Meta:
        abstract = True
        
    def __str__(self) -> str:
        return f"{self.type} - {self.text}"


class IndexPageButton(Button):
    class Meta:
        verbose_name = "Кнопка на главной"
        verbose_name_plural = "Кнопки на главной"


class RestorauntPageButton(Button):
    class Meta:
        verbose_name = "Кнопка на странице ресторанов"
        verbose_name_plural = "Кнопки на странице ресторанов"


class ShopPageButton(Button):
    class Meta:
        verbose_name = "Кнопка на странице магазинов"
        verbose_name_plural = "Кнопки на странице магазинов"
