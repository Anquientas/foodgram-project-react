from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Класс, определяющий правада доуступа следующим образом:
    - просмотр - доступно всем;
    - остальные методы - доступно автору объекта или администратору.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.is_staff)


class IsCurrentUserOrAdminOrReadOnly(permissions.BasePermission):
    """
    Класс, определяющий правада доуступа следующим образом:
    - просмотр - доступно всем;
    - остальные методы - доступно авторизованному пользователю
                         или администратору.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.id == request.user.id or request.user.is_staff)
