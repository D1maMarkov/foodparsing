# Generated by Django 5.0 on 2024-11-10 14:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("food", "0029_shopcategory_alter_cityshop_city_alter_cityshop_shop_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="shopproduct",
            options={"verbose_name": "продукт в магазине", "verbose_name_plural": "продукты в магазине"},
        ),
        migrations.AddField(
            model_name="dishref",
            name="unique_key",
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="restorauntref",
            name="unique_key",
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="shopproduct",
            name="shop",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="food.cityshop",
                verbose_name="магазин",
            ),
        ),
    ]
