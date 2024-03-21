from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet
from djoser.serializers import UserSerializer

from .models import Subscribe
from api.permissions import IsCurrentUserOrAdminOrReadOnly
from api.paginations import ApiPagination
from .serializers import CustomUserSerializer
from recipes.serializers import SubscribeSerializer


User = get_user_model()


PASSWORD_CHANGE_SUCСESSFULLY = 'Пароль пользователя {user} успешно изменен!'
SUBSCRIBE_CREATE_SUCСESSFULLY = (
    'Подписка пользователя {user} на пользователя {author} успешно создана!'
)
SUBSCRIBE_ERROR = 'Объект не найден!'
SUBSCRIBE_DELETE_SUCСESSFULLY = (
    'Подписка пользователя {user} на пользователя {author} успешно удалена!'
)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsCurrentUserOrAdminOrReadOnly,)
    serializer_class = UserSerializer
    pagination_class = ApiPagination

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Функция получения персональных данных текущего пользователя."""
        user = request.user
        serializer = CustomUserSerializer(
            user,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        """Функция создания и удаления подписки."""
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=request.data,
                context={'request': request, 'author': author}
            )
            if serializer.is_valid():
                serializer.save(author=author, user=user)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                SUBSCRIBE_ERROR,
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscribe.objects.filter(author=author, user=user).exists():
            Subscribe.objects.get(author=author).delete()
            return Response(
                SUBSCRIBE_DELETE_SUCСESSFULLY.format(
                    user=user.username,
                    author=author.username
                ),
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            SUBSCRIBE_ERROR,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Функция получения подписок пользователя."""
        subscribes = Subscribe.objects.filter(user=request.user)
        pages = self.paginate_queryset(subscribes)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
