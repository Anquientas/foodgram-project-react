import re

from django.conf import settings
from django.core.exceptions import ValidationError


BANNED_SYNBOL_IN_USERNAME = (
    'Никнейм "{username}" содержит неразрешенные символы:\n{symbols}'
)
USERNAME_NOT_ENDPOINT_SUFFIX = (
    f'Использовать никнейм {settings.USER_ENDPOINT_SUFFIX} запрещено!'
)


def validate_username(username):
    """
    Функция валидирования поля никнейма
    кастомной модели пользователя (User).
    """
    if username == settings.USER_ENDPOINT_SUFFIX:
        raise ValidationError(
            {'username': USERNAME_NOT_ENDPOINT_SUFFIX},
        )
    banned_symbols = re.sub(r'[\w.@+-]', '', username)
    if banned_symbols:
        raise ValidationError(
            {'username': BANNED_SYNBOL_IN_USERNAME.format(
                username=username,
                symbols=''.join(set(banned_symbols))
            )},
        )
    return username
