from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import IngredientRecipe


DOWNLOAD_FILENAME = 'shopping_list.txt'


def shopping_cart_ingredients(self, request):
    """
    Функция скачивания списка продуктов
    для выбранных рецептов пользователя.
    """
    sum_ingredients_in_recipes = IngredientRecipe.objects.filter(
        recipe__shopping_cart__user=request.user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        amounts=Sum('amount', distinct=True)).order_by('amounts')

    shopping_list = (
        'Список игредиентов к покупке для приготолвения выбранных рецептов:\n'
    )
    for ingredient in sum_ingredients_in_recipes:
        shopping_list += (
            f'\t- {ingredient["ingredient__name"].capitalize()}: '
            f'{ingredient["amounts"]} '
            f'{ingredient["ingredient__measurement_unit"]};\n'
        )

    response = HttpResponse(
        shopping_list,
        content_type='text/plain'
    )
    response['Content-Disposition'] = (
        f'attachment; filename={DOWNLOAD_FILENAME}'
    )
    return response
