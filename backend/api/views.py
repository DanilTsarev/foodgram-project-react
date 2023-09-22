from io import BytesIO
from pathlib import Path

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipe.models import (
    Favourite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AddInFavouriteSerializer,
    CreateRecipeSerializer,
    FollowListSerializer,
    IngredientSerializer,
    TagSerializer,
    TakeRecipeSerializer,
    UserSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = IngredientFilter
    filterset_fields = ('name',)
    ordering_fields = ('name',)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'PUT']:
            return CreateRecipeSerializer
        return TakeRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe(Favourite, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_recipe(Favourite, request, kwargs.get('pk'))

    @action(
        detail=True,
        methods=['POST', 'DELETE', 'GET'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.delete_recipe(ShoppingCart, request, kwargs.get('pk'))

    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(recipe=recipe, user=request.user).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance = model.objects.create(user=request.user, recipe=recipe)
        serializer = AddInFavouriteSerializer(
            instance, context={'request': request}
        )
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=request.user, recipe=recipe).exists():
            model.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=['GET'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            IngredientInRecipe.objects.filter(recipe__shopping_cart__user=user)
            .values_list('ingredient__name', 'ingredient__measurement_unit')
            .order_by('ingredient__name')
            .annotate(ingredient_sum=Sum('amount'))
        )

        buffer = BytesIO()

        font_path = (
            Path(__file__).resolve().parent / 'front' / 'arialmt.ttf'
        ).resolve()

        pdfmetrics.registerFont(TTFont('arialmt', font_path))

        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont('arialmt', 12)

        title = 'Корзина покупок'
        title_font = 'arialmt'
        title_size = 24
        p.setFont(title_font, title_size)
        title_width = p.stringWidth(title, title_font, title_size)
        title_x = (letter[0] - title_width) / 2
        title_y = 750
        p.drawString(title_x, title_y, title)

        y = 700
        for ingredient in ingredients:
            name, measurement_unit, amount = (
                ingredient[0],
                ingredient[1],
                ingredient[2],
            )
            y -= 20
            p.drawString(100, y, f'{name} - {amount} {measurement_unit}')

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(content_type='application/pdf')

        return response


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    additional_serializer = FollowListSerializer

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        authors = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(authors)
        serializer = self.additional_serializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=kwargs.get('id'))
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Вы не можете подписываться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscribe = Follow.objects.create(user=user, author=author)
            serializer = self.additional_serializer(
                subscribe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if user == author:
                return Response(
                    {'errors': 'Имена пользователя и автора совпадают'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            follow = Follow.objects.filter(user=user, author=author)
            if follow.exists():
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'У вас нет подписки на такого автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=['GET'], detail=False)
    def me(self, request):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        else:
            return Response(
                {'detail': 'Пользователь не авторизован'}, status=401
            )
