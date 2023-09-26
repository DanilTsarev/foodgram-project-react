from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from recipe.const import MAX_LENGTH_EMAIL, MAX_LENGTH_USER


class User(AbstractUser):
    username = models.CharField(
        'Ник пользователя',
        help_text='Ник пользователя',
        max_length=MAX_LENGTH_USER,
        blank=False,
        unique=True,
    )
    email = models.EmailField(
        'Почта',
        help_text='Электронная почта пользователя',
        blank=False,
        unique=True,
        max_length=MAX_LENGTH_EMAIL,
    )
    first_name = models.CharField(
        'Имя',
        help_text='Имя пользователя',
        max_length=MAX_LENGTH_USER,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        'Фамилия',
        help_text='Фамилия пользователя',
        max_length=MAX_LENGTH_USER,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        help_text='Пользователь, который подписался',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        help_text='Автор на которого подписался пользователь',
    )

    def save(self, *args, **kwargs):
        # Проверяем, подписан ли пользователь на автора.
        if Follow.objects.filter(user=self.user, author=self.author).exists():
            # Если подписан, не сохраняем эту связь.
            return

        # Если же такой связи нет, то сохраняем, делаем запись в БД.
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Подписка'
        constraints = [
            UniqueConstraint(fields=['user', 'author'], name='unique_follow')
        ]
