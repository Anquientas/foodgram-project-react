from django.db import models

from .validators import validate_color, validate_slug


MAX_LENGTH_NAME = 200
MAX_LENGTH_COLOR = 7
MAX_LENGTH_SLUG = 200


class Tag(models.Model):
    """Класс тега."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME,
        help_text='Введите название тега'
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=MAX_LENGTH_COLOR,
        validators=(validate_color,),
        help_text='Введите цвет в HEX-формате'
    )
    slug = models.CharField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        validators=(validate_slug,),
        help_text='Введите уникальный слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return (
            f'Название: {self.name[:20]}, '
            f'id: {self.pk}, '
            f'цвет: {self.color}, '
            f'слаг: {self.slug[:20]}, '
        )
