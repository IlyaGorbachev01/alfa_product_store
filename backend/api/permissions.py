"""Модуль с кастомными разрешениями."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsOwner(BasePermission):
    """
    Разрешение для проверки, является ли пользователь владельцем объекта.
    Предполагается, что объект имеет атрибут 'user'.
    """

    def has_object_permission(self, request: Request, view, obj) -> bool:
        """Проверяет, является ли пользователь владельцем объекта."""
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False
