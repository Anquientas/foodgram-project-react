from django.db.models import Sum

from recipes.models import IngredientRecipe, Recipe


def shopping_cart_ingredients(user):
    """
    Функция скачивания списка покупки продуктов
    для выбранных рецептов пользователя.
    """
    sum_ingredients_in_recipes = IngredientRecipe.objects.filter(
        recipe__shopping_carts__user=user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        amounts=Sum('amount', distinct=True)).order_by('amounts')

    recipes_in_shopping_carts = Recipe.objects.filter(
        shopping_carts__user=user
    ).values_list(
        'name',
        flat=True
    )

    ingredients = []
    numerate = 1
    for ingredient in sum_ingredients_in_recipes:
        ingredients.append(
            f'\t{numerate}) {ingredient["ingredient__name"].capitalize()}: '
            f'{ingredient["amounts"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
        )
        numerate += 1

    recipes = []
    numerate = 1
    for recipe in recipes_in_shopping_carts:
        recipes.append(f'\t{numerate}) {recipe}\n')
        numerate += 1

    return ''.join([
        'Список продуктов к покупке:\n',
        *map(str, ingredients),
        '\n\nПродукты необходимы для приготовления следующих рецептов:\n',
        *map(str, recipes)
    ])
