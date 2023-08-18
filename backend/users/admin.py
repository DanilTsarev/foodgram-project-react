from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "bio",
        "confirmation_code",
        "role",
    )
    list_editable = ("role",)
    search_fields = ("username",)
    list_filter = ("username", "role")
    empty_value_display = "-пусто-"
