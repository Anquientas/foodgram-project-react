from datetime import date

from django.db.models import Sum

from recipes.models import IngredientRecipe, Recipe


def shopping_cart_ingredients(user):
    """
    Функция скачивания списка покупки продуктов
    для выбранных рецептов пользователя.
    """
    sum_ingredients_in_recipes = IngredientRecipe.objects.filter(
        recipe__shoppingcarts__user=user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        amounts=Sum('amount', distinct=True)).order_by('amounts')
    recipes_in_shopping_carts = Recipe.objects.filter(
        shoppingcarts__user=user
    ).values_list(
        'name',
        flat=True
    )
    return '\n'.join([
        f'Список продуктов к покупке на {date.today().strftime("%d-%m-%Y")}:',
        *[
            f'{numerate}) '
            f'{ingredient["ingredient__name"].capitalize()}: '
            f'{ingredient["amounts"]} '
            f'{ingredient["ingredient__measurement_unit"]}'
            for numerate, ingredient in enumerate(
                sum_ingredients_in_recipes,
                start=1
            )
        ],
        '',
        'Продукты необходимы для приготовления следующих рецептов:',
        *[
            f'{numerate}) {recipe}'
            for numerate, recipe in enumerate(
                recipes_in_shopping_carts,
                start=1
            )
        ]
    ])
