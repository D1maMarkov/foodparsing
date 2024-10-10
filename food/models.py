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


class Food(models.Model):
    name = models.CharField(max_length=100, verbose_name="кухня")
    slug = models.CharField(max_length=100, null=True)
    genitive_case = models.CharField(max_length=100, null=True)
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Кухня"
        verbose_name_plural = "Кухни"


class CityFood(models.Model):
    city = models.ForeignKey(City, verbose_name="город", on_delete=models.CASCADE, related_name="foods")
    food = models.ForeignKey(Food, verbose_name="кухня", on_delete=models.CASCADE, related_name="city_foods")
    
    def __str__(self):
        return f"{self.city.name}-{self.food.name}"


class Restoraunt(models.Model):
    name = models.CharField(max_length=150, verbose_name="Ресторан")
    slug = models.CharField(max_length=150, null=True)
    city = models.ForeignKey(City, verbose_name="Город", on_delete=models.CASCADE, null=True, related_name="restoraunts")

    image = models.CharField(null=True, verbose_name="Картинка", max_length=2000)
    owner = models.TextField(max_length=7000, null=True)
    schedule = models.CharField(max_length=300, null=True)
    address = models.CharField(max_length=500, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"


class DishCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Категория блюд")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория блюда"
        verbose_name_plural = "Категории блюд"


class Dish(models.Model):
    name = models.CharField(max_length=200, verbose_name="Блюдо")
    restoraunt = models.ForeignKey(Restoraunt, on_delete=models.CASCADE, verbose_name="Заведение", related_name="dishes")
    image = models.URLField(max_length=1000, verbose_name="Изображение", null=True)
    slug = models.CharField(max_length=200, null=True)
    category = models.ForeignKey(DishCategory, verbose_name="категория", on_delete=models.CASCADE, null=True, related_name="dishes")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        
        indexes = [
            models.Index(
                fields=[
                    "id", "restoraunt_id", "category_id"
                ]
            )
        ]

class RestorauntDish(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="dish_restoraunts")
    restoraunt = models.ForeignKey(Restoraunt, on_delete=models.CASCADE)


class RestorauntFood(models.Model):
    restoraunt = models.ForeignKey(Restoraunt, on_delete=models.CASCADE, related_name="foods")
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="restoraunt_foods")


class Seo(models.Model):
    PAGE_TYPES = [
        ("Главная", "Главная"),
        ("Город", "Город"),
        ("Ресторан", "Ресторан"),
    ]
    page_type = models.CharField(max_length=100, choices=PAGE_TYPES, verbose_name="страница")
    title = models.CharField(max_length=300)
    description = models.TextField(max_length=3000)
    
    class Meta:
        verbose_name = "Seo"
        verbose_name_plural = "Seo"

    def __str__(self):
        return self.page_type