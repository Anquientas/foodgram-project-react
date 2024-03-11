import re

from django.core.exceptions import ValidationError


BANNED_SYNBOL_IN_SLUG = (
    'Слаг "{slug}" содержит неразрешенные символы:\n{symbols}'
)


def validate_slug(slug):
    # Убедится в верности записи запрещенных символов
    banned_symbols = re.sub(r'^[-a-zA-Z0-9_]+$', '', slug)
    if banned_symbols:
        raise ValidationError(
            {'slug': BANNED_SYNBOL_IN_SLUG.format(
                slug=slug,
                symbols=''.join(set(banned_symbols))
            )},
        )
    return slug
