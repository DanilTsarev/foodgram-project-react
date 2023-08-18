from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User
from users.permissions import IsAdmin
from users.serializers import SignUpSerializer, TokenSerializer, UserSerializer


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    username = request.data.get("username")
    email = request.data.get("email")

    if User.objects.filter(username=username, email=email).exists():
        return Response(request.data, status=status.HTTP_200_OK)

    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    send_confirmation_email(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


def send_confirmation_email(user):
    confirmation_code = default_token_generator.make_token(user)
    subject = "Код потверждения с сайта"
    message = f"Код для токена: {confirmation_code}"
    recipient_list = [user.email]

    send_mail(subject, message, from_email=None, recipient_list=recipient_list)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def token_jwt(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data["username"]
    confirmation_code = serializer.validated_data["confirmation_code"]

    user = get_object_or_404(User, username=username)

    if default_token_generator.check_token(user, confirmation_code):
        token = generate_jwt_token(user)
        return Response({"token": token}, status=status.HTTP_200_OK)

    return Response(
        {"detail": "Invalid confirmation code."},
        status=status.HTTP_400_BAD_REQUEST,
    )


def generate_jwt_token(user):
    token = AccessToken.for_user(user)
    return str(token)


class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset для обработки операций, связанных с пользователями.

    Доступные методы HTTP: GET, POST, PATCH, DELETE.

    Атрибуты:
        queryset: Queryset объектов User.
        serializer_class: Класс сериализатора для объектов User.
        http_method_names: Разрешенные методы HTTP.
        permission_classes: Классы разрешений для аутентификации и авторизации.
        filter_backends: Backend-ы фильтрации объектов User.
        search_fields: Поля для поиска объектов User.
        lookup_field: Поле для поиска объектов User.
        pagination_class: Класс пагинации для пагинации объектов User.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username"]
    lookup_field = "username"
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
        url_name="me",
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        """
        Получение и обновление информации о текущем пользователе.

        Если метод запроса - GET, возвращает сериализованные данные
        о текущем пользователе.

        Если метод запроса - PATCH, обновляет информацию
        о текущем пользователе на основе предоставленных данных.
        Перед сохранением данных выполняется проверка их валидности.
        Если в сериализованных данных присутствует поле 'role',
        оно удаляется из данных перед сохранением,
        чтобы предотвратить изменение поля 'role' обычными пользователями.

        Возвращает:
            Ответ, содержащий сериализованные данные пользователя.

        Вызывает:
            APIException: Если данные запроса недопустимы.
        """
        user = self.request.user

        if request.method == "GET":
            serializer = UserSerializer(request.user)

            return Response(serializer.data)

        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get("role"):
            serializer.validated_data.pop("role")
        serializer.save()

        return Response(serializer.data)
