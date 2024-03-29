from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)
from rest_framework.response import Response
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet
)

from djoser.serializers import SetPasswordSerializer
from djoser.serializers import UserCreateSerializer as UserCreateSerializerBase
from djoser.views import UserViewSet as UserViewSetBase

from .filters import RecipeFilter, IngredientFilter
from .paginations import ApiPagination
from .permissions import IsAuthorOrAdminOrReadOnlyPermission
from .serializers import (
    UserSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    RecipeSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    SubscribeCreateSerializer,
    TagSerializer
)
from .utils import shopping_cart_ingredients
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Favorite,
    ShoppingCart,
    Subscribe
)


User = get_user_model()


SUBSCRIBE_ERROR = 'Объект не найден!'
SUBSCRIBE_ERROR_VALIDATION = (
    'Ошибка валидации!\n'
    'Данные, поступившие в POST-запросе не прошли валидацию!'
)

RECIPE_NOT_FOUND = 'Рецепт с id={id} не найден!'

ADD_ERROR = (
    'Запись рецепта {recipe} и пользователя {user} уже есть!'
)
NOT_FOUND = (
    'Запись рецепта {recipe} и пользователя {user} не найдена!'
)

SHOPPING_CART_NONE = (
    'Список покупок пользователя {user} пуст!'
)
DOWNLOAD_FILENAME = 'shopping_list.txt'


class UserViewSet(UserViewSetBase):
    queryset = User.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnlyPermission,)
    serializer_class = UserSerializer
    pagination_class = ApiPagination

    def get_permissions(self):
        if self.request.method == 'GET' and self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super(UserViewSetBase, self).get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'POST' and self.action == 'create':
            self.serializer_class = UserCreateSerializerBase
        elif self.request.method == 'POST' and self.action == 'set_password':
            self.serializer_class = SetPasswordSerializer
        return super(UserViewSetBase, self).get_serializer_class()

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
            serializer = SubscribeCreateSerializer(
                data={'user': user.id, 'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                serializer.save(author=author, user=user)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                SUBSCRIBE_ERROR_VALIDATION,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SubscribeCreateSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        get_object_or_404(Subscribe, author=author, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Функция получения подписок пользователя."""
        subscribes = User.objects.filter(signers__user=request.user)
        pages = self.paginate_queryset(subscribes)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели продукта."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = (
        IsAuthorOrAdminOrReadOnlyPermission,
        IsAuthenticatedOrReadOnly
    )
    http_method_names = ('get', 'head', 'options', 'patch', 'post', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = ApiPagination

    def get_serializer_class(self):
        """Функция выбора сериализатора в зависимости от метода запроса."""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, *args, **kwargs):
        """
        Функция обработки запросов,
        связанных с избранными рецептами у текущего пользователя.
        """
        if request.method == 'POST':
            return self.add_pecipe_to_user(
                Favorite,
                FavoriteSerializer,
                request.user,
                kwargs.get('pk')
            )
        else:
            return self.delete_recipe_from_user(
                Favorite,
                request.user,
                kwargs.get('pk')
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, *args, **kwargs):
        """
        Функция обработки запросов,
        связанных с рецептами в списке покупок у текущего пользователя.
        """
        if request.method == 'POST':
            return self.add_pecipe_to_user(
                ShoppingCart,
                ShoppingCartSerializer,
                request.user,
                kwargs.get('pk')
            )
        else:
            return self.delete_recipe_from_user(
                ShoppingCart,
                request.user,
                kwargs.get('pk')
            )

    def add_pecipe_to_user(self,
                           model,
                           serializer,
                           user,
                           id_recipe):
        """
        Функция добавления записи в промежуточную таблицу
        для переданной модели.
        """
        recipe = get_object_or_404(Recipe, id=id_recipe)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': ADD_ERROR.format(
                    recipe=recipe.name,
                    user=user.username
                )},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = serializer(data={'recipe': id_recipe})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

    def delete_recipe_from_user(self,
                                model,
                                user,
                                id_recipe):
        """
        Функция удаления записи из промежуточной таблицы
        для переданной модели.
        """
        recipe = get_object_or_404(Recipe, id=id_recipe)
        get_object_or_404(model, user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        """Функция скачивания списка покупок."""
        user = User.objects.get(id=request.user.pk)
        if user.shopping_carts.exists():
            text = shopping_cart_ingredients(request.user)
            response = FileResponse(
                text,
                as_attachment=True,
                filename=f'{DOWNLOAD_FILENAME}'
            )
            return response
        return Response(
            SHOPPING_CART_NONE.format(
                user=user.username
            ),
            status=status.HTTP_404_NOT_FOUND
        )
