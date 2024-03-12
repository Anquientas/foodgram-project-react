from django.core.exceptions import ValidationError


MINIMUM_TIME_IN_COOKING_TIME = (
    'Время приготовления должно быть не менее 1 мин! '
    'Текущее значение "{time}" недопустимо.'
)


def validate_cooking_time(cooking_time):
    if cooking_time < 1:
        raise ValidationError(
            {'cooking_time': MINIMUM_TIME_IN_COOKING_TIME.format(
                time=cooking_time
            )},
        )
    return cooking_time
