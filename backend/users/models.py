from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


MAX_LENGTH_USERNAME = 150
MAX_LENGTH_EMAIL = 150
MAX_LENGTH_FIRSTNAME = 150
MAX_LENGTH_LASTNAME = 150
MAX_LENGTH_PASSWORD = 150
LENGTH_CONFIRMATION_CODE = 150


class User(AbstractUser):
    """Класс кастомного пользователя."""

    username = models.CharField(
        verbose_name='Никнейм',
        unique=True,
        max_length=MAX_LENGTH_USERNAME,
        validators=(validate_username,)
    )
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        max_length=MAX_LENGTH_EMAIL,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        blank=True,
        max_length=MAX_LENGTH_FIRSTNAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        blank=True,
        max_length=MAX_LENGTH_LASTNAME,
    )
    password = models.CharField(
        verbose_name='Пароль',
#        blank=True,
        max_length=MAX_LENGTH_PASSWORD,
    )
    is_subscribed = models.BooleanField(
        verbose_name='Подписка',
#        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return (
            f'Никнейм: {self.username[:20]}, '
            f'e-mail: {self.email}, '
            f'id: {self.pk}, '
        )
