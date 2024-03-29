from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from colorama import Style

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
        'password',
        'first_name',
        'last_name',
        'recipes_count',
        'signers_count',
        'signedes_count'
    )
    list_editable = (
        'username',
        'email',
        'password',
        'first_name',
        'last_name'
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = ('email',)

    def recipes_count(self, user):
        return user.recipes.count()

    def signedes_count(self, user):
        return user.signedes.count()

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

    list_display = ('id', 'name', 'slug', 'colored_color')
    list_editable = ('slug',)
    search_fields = ('name', 'slug')
    list_filter = ('slug',)

    @staticmethod
    def rgb_to_ansi(r, g, b):
        return f"\x1B[38;2;{r};{g};{b}m"

    def colored_color(self, tag):
        rgb_color = tuple(
            int(tag.color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)
        )
        return self.rgb_to_ansi(*rgb_color) + tag.color + Style.RESET_ALL
    colored_color.short_description = 'color'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ-зона для игредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('measurement_unit',)
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name',)


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
        'image',
        'count_favorites'
    )
    search_fields = ('name', 'tags')
    list_filter = ('cooking_time',)
    filter_horizontal = ('ingredients', 'tags')
    list_display_links = ('id',)

    def display_tags(self, recipe):
        return ", ".join([tag.name for tag in recipe.tags.all()])

    def display_ingredients(self, recipe):
        return ", ".join([
            ingredient.name for ingredient in recipe.ingredients.all()
        ])

    def cooking_time(self, recipe):
        return recipe.cooking_time

    def count_favorites(self, recipe):
        return recipe.favorites.count()


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Админ-зона для продуктов рецептов."""

    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
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
