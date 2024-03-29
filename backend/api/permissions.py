from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrAdminOrReadOnlyPermission(BasePermission):
    """
    Класс, определяющий правада доступа следующим образом:
    - просмотр - доступно всем;
    - остальные методы - доступно авторизованному пользователю
                         или администратору.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
