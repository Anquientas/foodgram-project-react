import os
import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


FILE_PATH_TAGS = 'data/tags.csv'
FILE_PATH_INGREDIENTS = 'data/ingredients.csv'


IMPORT_SUCCESSFULLY = 'Файл с {objects} успешно импортирован в базу данных.'
INGREDIENTS = 'ингредиентами'
FILE_NOT_FOUND = (
    'Файл с {objects} для загрузки не обнаружен! '
    'Указанный путь до файла: {file_path}'
)
TAGS = 'тегами'


class Command(BaseCommand):

    def check_file(self, file_path):
        return os.path.exists(file_path)

    def message_success(self, objects):
        self.stdout.write(self.style.SUCCESS(
            IMPORT_SUCCESSFULLY.format(objects=objects)
        ))

    def message_error(self, objects, file_path):
        self.stderr.write(self.style.ERROR(
            FILE_NOT_FOUND.format(
                objects=objects,
                file_path=file_path
            )
        ))

    def load_tags(self, data_file):
        with open(data_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            tags = []
            for row in reader:
                tags.append(Tag(
                    name=row[0],
                    color=row[1],
                    slug=row[2]
                ))
            Tag.objects.bulk_create(tags)

    def load_ingredients(self, data_file):
        with open(data_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            ingredients = []
            for row in reader:
                ingredients.append(Ingredient(
                    name=row[0],
                    measurement_unit=row[1]
                ))
            Ingredient.objects.bulk_create(ingredients)

    def handle(self, *args, **options):
        if self.check_file(FILE_PATH_TAGS):
            self.load_tags(FILE_PATH_TAGS)
            self.message_success(TAGS)
        else:
            self.message_error(TAGS, FILE_PATH_TAGS)

        if self.check_file(FILE_PATH_INGREDIENTS):
            self.load_ingredients(FILE_PATH_INGREDIENTS)
            self.message_success(INGREDIENTS)
        else:
            self.message_error(INGREDIENTS, FILE_PATH_INGREDIENTS)
