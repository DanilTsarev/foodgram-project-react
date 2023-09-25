from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipe.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import Follow, User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.follower.filter(author=obj).exists()
        )


class IngredientTakeRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'measurement_unit', 'name', 'amount')
        read_only = ('id', 'measurement_unit', 'name')


class IngredientInCreateRecipeSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        fields = (
            'id',
            'amount',
        )


class TakeRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientTakeRecipeSerializer(
        source='ingredients_for_recipes', many=True
    )
    author = UserSerializer()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'text',
            'image',
            'cooking_time',
            'ingredients',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, recipe):
        request = self.context.get('request')

        return (
            request.user.is_authenticated
            and request.user.favorites.filter(recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.shopping_cart.filter(recipe=recipe).exists()
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngredientInCreateRecipeSerializer(
        many=True,
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField(represent_in_base64=True)
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(1, message="Минимальное значение: 1"),
            MaxValueValidator(999, message="Максимальное значение: 999"),
        ]
    )

    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'text',
            'image',
            'cooking_time',
            'ingredients',
            'tags',
        )

    def create_ingredients_in_recipe(self, recipe, ingredients):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    ingredient=ingredient['id'],
                    recipe=recipe,
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_in_recipe(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )

        tags_data = validated_data.get('tags', [])
        recipe.tags.set(tags_data)

        ingredients = validated_data.get('ingredients', [])
        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients_in_recipe(recipe, ingredients)

        super().update(recipe, validated_data)

        return recipe

    def validate(self, attrs):
        tags = attrs.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Выберите хотя бы один тег для рецепта.'
            )

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError('Теги не должны повторяться.')

        ingredients_data = attrs.get('ingredients')
        if not ingredients_data:
            raise serializers.ValidationError(
                'Выберите хотя бы один ингредиент для рецепта.'
            )

        ingredient_ids = [ingredient['id'] for ingredient in ingredients_data]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )

        return attrs

    def to_representation(self, instance):
        return TakeRecipeSerializer(
            instance,
            context=self.context,
        ).data


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = fields


class FollowListSerializer(UserSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Follow
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[: int(limit)]
        return RecipeSubscribeSerializer(queryset, many=True).data

    def validate(self, attrs):
        author = attrs.get('author')
        user = attrs.get('user')
        if author == user:
            raise serializers.ValidationError(
                'Вы не можете подписываться на самого себя',
            )
        if user.following.filter(author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя',
            )
        return attrs


class AddInFavouriteSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
