"""Конфигурации админ-зоны приложения users."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройки отображения кастомной модели в админ-панели."""

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('bio', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('email', 'bio', 'role')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
