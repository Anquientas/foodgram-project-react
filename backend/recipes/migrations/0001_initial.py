# Generated by Django 3.2.16 on 2024-03-14 18:53

from django.db import migrations, models
import django.db.models.deletion
import recipes.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название ингредиента', max_length=200, verbose_name='Название')),
                ('measurement_unit', models.CharField(help_text='Введите единицу измерения', max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(help_text='Введите количество ингредиента', validators=[recipes.validators.validate_amount], verbose_name='Количество игредиента')),
            ],
            options={
                'verbose_name': 'Ингридиенты рецепта',
                'verbose_name_plural': 'Ингридиенты рецептов',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название рецепта', max_length=200, verbose_name='Название рецепта')),
                ('text', models.TextField(help_text='Введите описание рецепта', verbose_name='Описание рецепта')),
                ('cooking_time', models.PositiveSmallIntegerField(help_text='Введите время приготовления рецепта в минутах', validators=[recipes.validators.validate_cooking_time], verbose_name='Время приготовления')),
                ('image', models.ImageField(help_text='Добавьте изображение готового блюда', upload_to='recipe/images/', verbose_name='Изображение готового блюда')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Введите название тега', max_length=200, verbose_name='Название')),
                ('color', models.CharField(help_text='Введите цвет в HEX-формате', max_length=7, validators=[recipes.validators.validate_color], verbose_name='Цвет в HEX')),
                ('slug', models.CharField(help_text='Введите уникальный слаг', max_length=200, unique=True, validators=[recipes.validators.validate_slug], verbose_name='Уникальный слаг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Введите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
    ]
