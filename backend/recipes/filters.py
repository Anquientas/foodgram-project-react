from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (
    ModelMultipleChoiceFilter,
    NumberFilter
)

from .models import Recipe, Tag


User = get_user_model()


class RecipeFilter(FilterSet):
    """Класс фильтра для модели рецепта."""

    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = NumberFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = NumberFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags__slug'
        )

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
