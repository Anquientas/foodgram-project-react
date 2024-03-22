from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username
from backend.settings import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_FIRSTNAME,
    MAX_LENGTH_LASTNAME,
    MAX_LENGTH_PASSWORD,
    MAX_LENGTH_USERNAME
)


class User(AbstractUser):
    """Класс кастомного пользователя."""

    username = models.CharField(
        verbose_name='Никнейм',
        unique=True,
        max_length=MAX_LENGTH_USERNAME,
        validators=(validate_username,),
        help_text='Введите никнейм'
    )
    email = models.EmailField(
        verbose_name='E-mail',
        unique=True,
        max_length=MAX_LENGTH_EMAIL,
        help_text='Введите свой e-mail'
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH_FIRSTNAME,
        help_text='Введите свое имя'
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_LASTNAME,
        help_text='Введите свою фамилию'
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_LENGTH_PASSWORD,
        help_text='Введите пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return (
            f'Никнейм: {self.username[:20]}, '
            f'e-mail: {self.email[:20]}, '
            f'id: {self.pk}.'
        )


class Subscribe(models.Model):
    """
    Подписка на пользователей.
    Комбинация автора рецепта и пользователя уникальна.
    Автор не может подписываться на самого себя.
    """

    author = models.ForeignKey(
        User,
        verbose_name='Подписка на автора рецепта',
        related_name='signed',
        on_delete=models.CASCADE,
        help_text='Подписаться на автора рецепта'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='signer',
        on_delete=models.CASCADE,
        help_text='Текущий пользователь'
    )

    class Meta:
        verbose_name = 'Мои подписки'
        verbose_name_plural = 'Мои подписки'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author_and_user',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_user_is_author',
            )
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user.username} (id: {self.user.id}) '
            f'подписан на {self.author.username} (id: {self.author.id}).'
        )
