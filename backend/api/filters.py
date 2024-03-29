from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (
    ModelMultipleChoiceFilter,
    NumberFilter
)

from recipes.models import Recipe, Tag


User = get_user_model()


class RecipeFilter(FilterSet):
    """Класс фильтра для модели рецепта."""

    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = NumberFilter(
        method='is_favorited_get',
    )
    is_in_shopping_cart = NumberFilter(
        method='is_in_shopping_cart_get',
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags__slug'
        )

    def is_favorited_get(self, recipes, name, value):
        if self.request.user.is_authenticated and value:
            return recipes.filter(favorites__user=self.request.user)
        return recipes

    def is_in_shopping_cart_get(self, recipes, name, value):
        if self.request.user.is_authenticated and value:
            return recipes.filter(shopping_carts__user=self.request.user)
        return recipes
