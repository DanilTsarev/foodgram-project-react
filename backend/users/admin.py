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
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'image',
        'cooking_time',
    )
    list_editable = ('image',)
    search_fields = ('author__username',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'

    def tags_display(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    tags_display.short_description = 'Tags'


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
