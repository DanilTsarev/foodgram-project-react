from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from recipe.models import (
    Favourite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_superuser',
    )
    list_editable = ('first_name', 'last_name', 'is_superuser')
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'username',
        'email',
    )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'image',
        'cooking_time',
        'tags_2',
        'favorite',
    )
    list_editable = ('image',)
    search_fields = ('author', 'name', 'tags_2')
    list_filter = (
        'name',
        'author',
        'tags',
    )
    empty_value_display = '-пусто-'

    @admin.display(description='теги')
    def tags_2(self, recipe):
        return [tag.name for tag in recipe.tags.all()]

    @admin.display(description='Кол-во добавления в избранное')
    def favorite(self, recipe):
        return recipe.favorites.count()


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = (
        'name',
        'measurement_unit',
    )
    list_editable = ('measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagResource(resources.ModelResource):
    class Meta:
        model = Tag


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_class = TagResource
    list_display = (
        'name',
        'color',
        'slug',
    )
    list_editable = ('color',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    empty_value_display = '-пусто-'


admin.site.unregister(auth_admin.Group)
