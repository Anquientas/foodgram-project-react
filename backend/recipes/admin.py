from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.utils.safestring import mark_safe

from .filters import CookingTimeFilter
from .models import (
    Ingredient,
    IngredientRecipe,
    Favorite,
    Recipe,
    ShoppingCart,
    Subscribe,
    Tag,
)


User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdminBase):
    """Админ-зона для пользователей."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'recipes_count',
        'signers_count',
        'authors_count'
    )
    list_editable = (
        'first_name',
        'last_name'
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = ('signers',)

    @admin.display(description='Рецепты')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписки')
    def authors_count(self, user):
        return user.authors.count()

    @admin.display(description='Подписчики')
    def signers_count(self, user):
        return user.signers.count()


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Админ-зона для подписок."""

    list_display = ('author', 'user')
    list_filter = ('author', 'user')
    search_fields = ('author', 'user')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-зона для тегов."""

    list_display = ('id', 'name', 'slug', 'color', 'color_display')
    list_editable = ('name', 'color')
    search_fields = ('name',)
    list_filter = ('name',)

    @admin.display(description='Цвет')
    def color_display(self, tag):
        return mark_safe(
            f'<div style="background-color: {tag.color}; '
            'width: 15px; height: 15px"></div>'
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-зона для продуктов."""

    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-зона для рецептов."""

    list_display = (
        'id',
        'name',
        'author',
        'cooking_time',
        'display_tags',
        'display_ingredients',
        'image_display',
        'count_favorites',
        'created_at_display'
    )
    search_fields = ('name', 'tags')
    list_filter = ('author', 'tags', CookingTimeFilter)
    filter_horizontal = ('ingredients', 'tags')
    list_display_links = ('id',)
    inlines = (IngredientInline,)
    readonly_fields = ('image_display',)

    @admin.display(description='Теги')
    def display_tags(self, recipe):
        return mark_safe('<br>'.join(tag.name for tag in recipe.tags.all()))

    @admin.display(description='Продукты')
    def display_ingredients(self, recipe):
        return mark_safe('<br>'.join(
            f'{ingredient.ingredient.name[:20]} '
            f'{ingredient.amount} '
            f'{ingredient.ingredient.measurement_unit}'
            for ingredient in recipe.ingredients_recipes.all()
        ))

    @admin.display(description='В избранных')
    def count_favorites(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Изображение')
    def image_display(self, recipe):
        return mark_safe(f'<img src="{recipe.image.url}" height="50" />')

    @admin.display(description='Дата создания')
    def created_at_display(self, obj):
        return obj.created_at.strftime('%d %B %Y')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Админ-зона для продуктов рецептов."""

    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe',)
    search_fields = ('recipe', 'ingredient')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-зона для списков покупок."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ-зона для избранных рецептов."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


admin.site.empty_value_display = 'Не задано'
