from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Класс, определяющий правада доступа следующим образом:
    - просмотр - доступно всем;
    - остальные методы - доступно авторизованному пользователю
                         или администратору.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
