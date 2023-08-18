from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = "admin"
    USER = "user"
    USER_ROLES = [
        (USER, "user"),
        (ADMIN, "admin"),
    ]
    username = models.CharField(
        "Логин пользователя",
        help_text="Ник пользователя",
        max_length=150,
        blank=False,
        unique=True,
    )
    email = models.EmailField(
        "Почта",
        help_text="Электронная почта пользователя",
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        "Имя",
        help_text="Имя пользователя",
        max_length=150,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        "Фамилия",
        help_text="Фамилия пользователя",
        max_length=150,
        blank=True,
        null=True,
    )
    bio = models.TextField(
        "Немного о себе",
        help_text="Биография пользователя",
        blank=True,
        null=True,
    )
    confirmation_code = models.CharField(
        "Код подтверждения",
        help_text="Код подтверждения из письма",
        max_length=200,
    )
    role = models.CharField(
        "Роль",
        help_text="Роль пользователя",
        max_length=150,
        blank=False,
        choices=USER_ROLES,
        default="user",
    )

    USERNAME_FIELD = "email"  # Указываем уникальные поля
    REQUIRED_FIELDS = ["username"]  # при создании пользователя.

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        return self.username
