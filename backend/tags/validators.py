import re

from django.core.exceptions import ValidationError


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


def check_banned_symbols(template, text):
    return re.sub(template, '', text)


def validate_slug(slug):
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
    message = ''
    banned_symbols = re.sub(r'[a-z\d]+$\b', '', color[1:])
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