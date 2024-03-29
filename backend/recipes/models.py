from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator

from .validators import validate_username


BANNED_SYMBOL_IN_COLOR = (
    'Цвет в HEX-формате содержит недопустимые символы!'
)
MINIMUM_TIME_IN_COOKING_TIME = (
    'Время приготовления должно быть не менее 1 мин!'
)
MINIMUM_NUMBER_IN_AMOUNT = (
    'Мера должна быть не менее 1 единицы измерения!'
)


class User(AbstractUser):
    """Класс кастомного пользователя."""

    username = models.CharField(
        verbose_name='Никнейм',
        unique=True,
        max_length=settings.MAX_LENGTH_USERNAME,
        validators=(validate_username,),
        help_text='Введите никнейм'
    )
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        max_length=settings.MAX_LENGTH_EMAIL,
        help_text='Введите свой e-mail'
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LENGTH_FIRSTNAME,
        help_text='Введите свое имя'
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LENGTH_LASTNAME,
        help_text='Введите свою фамилию'
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.MAX_LENGTH_PASSWORD,
        help_text='Введите пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return (
            f'Никнейм: {self.username[:20]}, '
            f'e-mail: {self.email[:20]}, '
            f'id: {self.pk}.'
        )


class Subscribe(models.Model):
    """
    Подписка на пользователей.
    Комбинация автора рецепта и пользователя уникальна.
    Автор не может подписываться на самого себя.
    """

    author = models.ForeignKey(
        User,
        verbose_name='Подписка на автора рецепта',
        related_name='signedes',
        on_delete=models.CASCADE,
        help_text='Подписаться на автора рецепта'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='signers',
        on_delete=models.CASCADE,
        help_text='Текущий пользователь'
    )

    class Meta:
        verbose_name = 'Мои подписки'
        verbose_name_plural = 'Мои подписки'
        ordering = ('author',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author_and_user',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_user_is_author',
            )
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user.username} (id: {self.user.id}) '
            f'подписан на {self.author.username} (id: {self.author.id}).'
        )


class Tag(models.Model):
    """Класс тега."""

    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_LENGTH_NAME_TAG,
        help_text='Введите название тега'
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=settings.MAX_LENGTH_COLOR,
        validators=(RegexValidator(
            regex=r'/#([a-f0-9]{6}|[a-f0-9]{3})\b/gi',
            message=BANNED_SYMBOL_IN_COLOR
        ),),
        help_text='Введите цвет в HEX-формате'
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=settings.MAX_LENGTH_SLUG,
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
            f'слаг: {self.slug[:20]}.'
        )


class Ingredient(models.Model):
    """Класс продукта."""

    name = models.CharField(
        verbose_name='Название',
        max_length=settings.MAX_LENGTH_NAME_INGREDIENT,
        help_text='Введите название продукта'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.MAX_LENGTH_MEASUREMENT_UNIT,
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)

    def __str__(self):
        return (
            f'Название: {self.name[:20]}, '
            f'id: {self.pk}, '
            f'единица измерения: {self.measurement_unit[:20]}.'
        )


class Recipe(models.Model):
    """Класс рецепта."""

    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.MAX_LENGTH_NAME_RECIPE,
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
        verbose_name='Продукт',
        through='IngredientRecipe',
        help_text='Введите продукт'
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
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(1, MINIMUM_TIME_IN_COOKING_TIME),),
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
        default_related_name = 'recipes'

    def __str__(self):
        return (
            f'Название: {self.name[:20]}, '
            f'id: {self.pk}, '
            f'время приготовления: {self.cooking_time}.'
        )


class IngredientRecipe(models.Model):
    """
    Продукты для рецепта.
    Промежуточная модель для таблиц Recipe и Ingredient.
    Для одного рецепта ингридиенты не могут повторятся.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        help_text='Выберите рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Продукт',
        on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        help_text='Введите продукт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Мера',
        validators=(MinValueValidator(1, MINIMUM_NUMBER_IN_AMOUNT),),
        help_text='Введите меру'
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
            f'Рецепт: {self.recipe.name[:20]}, '
            f'продукт: {self.ingredient.name[:20]}, '
            f'количество: {self.amount}.'
        )


class CatalogBase(models.Model):
    """
    Базовый класс для списков избранного и покупок пользователя.
    Для одного пользователя рецепты в списках не могут повторятся.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        help_text='Введите пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        help_text='Введите рецепт'
    )

    class Meta:
        abstract = True


class ShoppingCart(CatalogBase):
    """
    Список покупок пользователя.
    Для одного пользователя рецепты в списке покупок не могут повторятся.
    """

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_cart_for_user',
            )
        ]
        default_related_name = "shopping_carts"

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name[:20]} (id: {self.recipe.id}) '
            'в списке покупок пользователя '
            f'{self.user.username[:20]} (id: {self.user.id}).'
        )


class Favorite(CatalogBase):
    """
    Список избранных рецептов пользователя.
    Для одного пользователя рецепты в списке покупок не могут повторятся.
    """

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorite_for_user',
            )
        ]
        default_related_name = "favorites"

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name[:20]} (id: {self.recipe.id}) '
            'в списке избранных пользователя '
            f'{self.user.username[:20]} (id: {self.user.id}).'
        )
