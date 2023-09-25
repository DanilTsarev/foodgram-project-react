from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User
from .const import MAX_LENGTH, MAX_LENGTH_HEX


class Ingredient(models.Model):
    name = models.CharField('Ингредиент', max_length=MAX_LENGTH)
    measurement_unit = models.CharField('Единица измерения', max_length=MAX_LENGTH)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit',
            ),
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название', unique=True, max_length=MAX_LENGTH)
    color = ColorField(
        unique=True,
        max_length=MAX_LENGTH_HEX,
    )
    slug = models.SlugField('Класс блюда', unique=True, max_length=MAX_LENGTH)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название рецепта', max_length=MAX_LENGTH)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )

    text = models.TextField('Описание')

    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        blank=True,
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1, message='Меньше, чем за 1 минуту ничего не сделать'
            )
        ],
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        blank=True,
        through='IngredientInRecipe',
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        blank=True,
        related_name='recipes',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_for_recipes',
        verbose_name='Рецепт',
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipes',
    )

    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1, message='Нужен хотя бы один ингредиент')
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ['amount']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient.name} ({self.recipe})'


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favourite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список для покупок'
        verbose_name_plural = 'Списки для покупок'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} будет готовить "{self.recipe}"'
