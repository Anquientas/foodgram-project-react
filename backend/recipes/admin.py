from django.contrib import admin

from .models import (
    Ingredient,
    IngredientRecipe,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag
)


class TagAdmin(admin.ModelAdmin):
    """Админ-зона для тегов."""

    list_display = ('id', 'name', 'slug', 'color')
    list_editable = ('slug', 'color')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug', 'color')


class IngredientAdmin(admin.ModelAdmin):
    """Админ-зона для игредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name', 'measurement_unit')


class RecipeAdmin(admin.ModelAdmin):
    """Админ-зона для рецептов."""

    list_display = ('id', 'name', 'author', 'cooking_time')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags', 'cooking_time')
    filter_horizontal = ('ingredients', 'tags')
    list_display_links = ('id',)


class IngredientRecipeAdmin(admin.ModelAdmin):
    """Админ-зона для ингредиентов рецептов."""

    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe', 'ingredient')


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ-зона для списков покупок."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


class FavoriteAdmin(admin.ModelAdmin):
    """Админ-зона для избранных рецептов."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


admin.site.empty_value_display = 'Не задано'

admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
