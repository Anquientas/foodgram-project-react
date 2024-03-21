import re

from django.core.exceptions import ValidationError


MINIMUM_NUMBER_IN_AMOUNT = (
    'Количество ингредиентов должно быть не менее 1 единицы измерения! '
    'Текущее значение "{amount}" недопустимо.'
)
MINIMUM_TIME_IN_COOKING_TIME = (
    'Время приготовления должно быть не менее 1 мин! '
    'Текущее значение "{time}" недопустимо.'
)
BANNED_SYMBOL_IN_COLOR = (
    'Цвет в HEX-формате "{color}" содержит недопустимые символы:\n{symbols}'
)
BANNED_SYMBOL_IN_SLUG = (
    'Слаг "{slug}" содержит неразрешенные символы:\n{symbols}'
)
LENGTH_IN_COLOR = (
    'Неверная длина строки цвета в HEX-формате "{color}"!\n'
    'Должно быть 4 или 7 символов, в строке {number} символов.'
)
ZERO_SYMBOL_IN_COLOR = (
    'Неверный формат строки цвета "{color}"!\n'
    'Должен быть HEX-формат, т.е. начинаться с "#", а не с {symbol}.'
)


def validate_amount(amount):
    """
    Функция валидирования поля количества ингредиента
    модели ингредиента в рецепте (IngredientRecipe).
    """
    if amount < 1:
        raise ValidationError(
            {'amount': MINIMUM_NUMBER_IN_AMOUNT.format(
                amount=amount
            )},
        )
    return amount


def validate_cooking_time(cooking_time):
    """
    Функция валидирования поля времени приготовления
    модели рецепта (Recipe).
    """
    if cooking_time < 1:
        raise ValidationError(
            {'cooking_time': MINIMUM_TIME_IN_COOKING_TIME.format(
                time=cooking_time
            )},
        )
    return cooking_time


def validate_slug(slug):
    """Функция валидирования поля слага модели тега (Tag)."""
    banned_symbols = re.sub(r'[-a-zA-Z0-9_]+$', '', slug)
    if banned_symbols:
        raise ValidationError(
            {'slug': BANNED_SYMBOL_IN_SLUG.format(
                slug=slug,
                symbols=''.join(set(banned_symbols))
            )},
        )
    return slug


def validate_color(color):
    """Функция валидирования поля цвета модели тега (Tag)."""
    message = ''
    banned_symbols = re.sub(r'[a-fA-F\d]+$\b', '', color[1:])
    if banned_symbols:
        message = BANNED_SYMBOL_IN_COLOR.format(
            color=color,
            symbols=''.join(set(banned_symbols))
        )

    indicator_two_errors = False
    if color[0] != '#':
        if message:
            message = (
                '1) ' + message + '\n\n2) ' + ZERO_SYMBOL_IN_COLOR.format(
                    color=color,
                    symbol=color[0]
                )
            )
            indicator_two_errors = True
        else:
            message = ZERO_SYMBOL_IN_COLOR.format(
                color=color,
                symbol=color[0]
            )

    if len(color) != 7 and len(color) != 4:
        if message and indicator_two_errors:
            message += '\n\n3) ' + LENGTH_IN_COLOR.format(
                color=color,
                number=len(color)
            )
        elif message and not indicator_two_errors:
            message = (
                '1) ' + message + '\n\n2) ' + LENGTH_IN_COLOR.format(
                        color=color,
                        number=len(color)
                    )
                )
        else:
            message = LENGTH_IN_COLOR.format(
                color=color,
                number=len(color)
            )

    if message:
        raise ValidationError(
            {'slug': message},
        )
    return color
