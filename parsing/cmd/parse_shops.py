import asyncio
import os

import django
import sys

# Получаем путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительскому каталогу
parent_dir_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
print(parent_dir_path)
# Добавляем путь к родительскому каталогу в sys.path
sys.path.append(parent_dir_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fooddelivery.settings")
django.setup()


def main():
    from parsing.parser import ShopsParser

    parser = ShopsParser()
    asyncio.run(parser())


if __name__ == "__main__":
    main()
