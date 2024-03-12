from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


MAX_LENGTH_USERNAME = 150
MAX_LENGTH_EMAIL = 150
MAX_LENGTH_FIRSTNAME = 150
MAX_LENGTH_LASTNAME = 150
MAX_LENGTH_PASSWORD = 150
LENGTH_CONFIRMATION_CODE = 150

AUTHOR_AND_USER_IS_NOT_UNIQUE = (
    'Пользователь и автор рецепта не могут повторяться! '
)
AUTHOR_NOT_SIGNER_TO_AUTHOR = (
    'Автор рецепта не может подписываться сам на себя!'
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
        blank=True,
        max_length=MAX_LENGTH_FIRSTNAME,
        help_text='Введите свое имя'
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        blank=True,
        max_length=MAX_LENGTH_LASTNAME,
        help_text='Введите свою фамилию'
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_LENGTH_PASSWORD,
        help_text='Введите пароль'
    )
#     is_subscribed = models.BooleanField(
#         verbose_name='Подписка',
#     )

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


class Subscribe(models.Model):
    """
    Подписка на пользователей.
    Комбинация автора рецепта и пользователя уникальна.
    Автор не может подписываться на самого себя.
    """

    author = models.ForeignKey(
        verbose_name='Подписка на автора рецепта',
        related_name='signed',
        help_text='Подписаться на автора рецепта'
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='signer',
        help_text='Текущий пользователь'
    )

    class Meta:
        verbose_name = 'Мои подписки'
        verbose_name_plural = 'Мои подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
                message=AUTHOR_AND_USER_IS_NOT_UNIQUE
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_user_is_author',
                message=AUTHOR_NOT_SIGNER_TO_AUTHOR
            ),
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user} подписан на {self.author}.'
        )
