from django.contrib.auth import get_user_model
from django.db import models

from .validators import (
    validate_amount,
    validate_cooking_time,
    validate_color,
    validate_slug
)


User = get_user_model()


MAX_LENGTH_NAME_RECIPE = 200

MAX_LENGTH_NAME_TAG = 200
MAX_LENGTH_COLOR = 7
MAX_LENGTH_SLUG = 200

MAX_LENGTH_NAME_INGREDIENT = 200
MAX_LENGTH_MEASUREMENT_UNIT = 200

INGREDIENT_IN_RECIPE_IS_NOT_UNIQUE = (
    'Ингредиенты в рецепте не могут повторятся!'
)
RECIPE_IN_SHOPPING_CART_IS_NOT_UNIQUE = (
    'Рецепты в списке покупок не могут повторятся!'
)
RECIPE_IN_FAVORITE_IS_NOT_UNIQUE = (
    'Рецепты в списке избранных не могут повторятся!'
)


class Tag(models.Model):
    """Класс тега."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME_TAG,
        help_text='Введите название тега'
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=MAX_LENGTH_COLOR,
        validators=(validate_color,),
        help_text='Введите цвет в HEX-формате'
    )
    slug = models.CharField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        validators=(validate_slug,),
        help_text='Введите уникальный слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return (
            f'Название: {self.name[:20]}, '
            f'id: {self.pk}, '
            f'цвет: {self.color}, '
            f'слаг: {self.slug[:20]}, '
        )


class Ingredient(models.Model):
    """Класс ингредиента."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME_INGREDIENT,
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_MEASUREMENT_UNIT,
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return (
            f'Название: {self.name[:20]}, '
            f'id: {self.pk}, '
            f'единица измерения: {self.measurement_unit[:20]}, '
        )


class Recipe(models.Model):
    """Класс рецепта."""

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_LENGTH_NAME_RECIPE,
        help_text='Введите название рецепта'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        help_text='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        through='IngredientRecipe',
        help_text='Введите ингредиент'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Название тега',
        help_text='Выберите тег'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(validate_cooking_time,),
        help_text='Введите время приготовления рецепта в минутах',
    )
    image = models.ImageField(
        verbose_name='Изображение готового блюда',
        upload_to='recipe/images/',
        help_text='Добавьте изображение готового блюда',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return (
            f'Название: {self.name[:20]}, '
            f'id: {self.pk}, '
            f'время приготовления: {self.cooking_time}, '
        )


class IngredientRecipe(models.Model):
    """
    Ингредиенты для рецепта.
    Промежуточная модель для таблиц Recipe и Ingredient.
    Для одного рецепта ингридиенты не могут повторятся.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        help_text='Выберите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        help_text='Введите ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество игредиента',
        validators=(validate_amount,),
        help_text='Введите количество ингредиента'
    )

    class Meta:
        verbose_name = 'Ингридиенты рецепта'
        verbose_name_plural = 'Ингридиенты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        return (
            f'Рецепт: {self.recipe}, '
            f'ингредиент: {self.ingredient}, '
            f'количество: {self.amount}'
        )


class ShoppingCart(models.Model):
    """
    Список покупок пользователя.
    Для одного пользователя рецепты в списке покупок не могут повторятся.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        help_text='Введите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        help_text='Введите рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_cart_for_user',
            )
        ]

    def __str__(self):
        return (
            f'Рецепт: {self.recipe}, в списке покупок '
            f'пользователя {self.user}.'
        )


class Favorite(models.Model):
    """
    Список избранных рецептов пользователя.
    Для одного пользователя рецепты в списке покупок не могут повторятся.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite',
        help_text='Введите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite',
        help_text='Введите рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorite_for_user',
            )
        ]

    def __str__(self):
        return (
            f'Рецепт: {self.recipe}, в списке избранных '
            f'пользователя {self.user}.'
        )
