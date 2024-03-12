from django.db import models

from .validators import validate_cooking_time
from ingredients.models import Ingredient
from tags.models import Tag


MAX_LENGTH_NAME = 200


class Recipe(models.Model):
    """Класс рецепта."""

    image = models.ImageField(
        upload_to='recipe/images/'
    )
    ingredients = models.ManyToManyField(Ingredient)
    tags = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME,
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=(validate_cooking_time,)
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return (
            f'Название: {self.name[:20]}, '
            f'id: {self.pk}, '
            f'время приготовления: {self.cooking_time}, '
        )
