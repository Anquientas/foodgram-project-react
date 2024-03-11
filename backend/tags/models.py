from django.db import models

from .validators import validate_color, validate_slug


MAX_LENGTH_NAME = 200
MAX_LENGTH_COLOR = 7
MAX_LENGTH_SLUG = 200


class Tag():
    """Класс тэга."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        blank=True,
        max_length=MAX_LENGTH_COLOR,
        validators=(validate_color,)
    )
    slug = models.CharField(
        verbose_name='Уникальный слаг',
        unique=True,
        max_length=MAX_LENGTH_SLUG,
        validators=(validate_slug,)
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return (
            f'Название: {self.name[:20]}, '
            f'цвет: {self.color}, '
            f'слаг: {self.slug[:20]}, '
            f'id: {self.pk}, '
        )
