from django.core.validators import MaxLengthValidator, RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(150),
            RegexValidator(
                regex=r"^[a-zA-Z0-9_-]+$",
                message="Letters, digits and @/./+/-/_ only.",
            ),
        ]
    )
    # Валидатор проверяет уникальность полей username и email.
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(254),
        ]
    )

    def validate_username(self, value):
        """
        Проверяет, что нельзя создать пользователя с ником "me".
        """
        if value.lower() == "me":
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value

    class Meta:
        fields = ("username", "email")
        model = User


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(150),
            RegexValidator(
                regex=r"^[a-zA-Z0-9_-]+$",
                message="Letters, digits and @/./+/-/_ only.",
            ),
        ],
        required=True,
    )
    # Валидатор проверяет уникальность полей username и email.
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(254),
        ]
    )

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        model = User
