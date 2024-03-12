from django.db import models


MAX_LENGTH_NAME = 200
MAX_LENGTH_MEASUREMENT_UNIT = 200


class Ingredient(models.Model):
    """Класс ингредиента."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME,
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_MEASUREMENT_UNIT,
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return (
            f'Название: {self.name[:20]}, '
            f'id: {self.pk}, '
            f'единица измерения: {self.measurement_unit[:20]}, '
        )
