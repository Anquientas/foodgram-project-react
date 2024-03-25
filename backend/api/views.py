from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    SAFE_METHODS
)
from rest_framework.response import Response
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet
)

from djoser.serializers import UserSerializer
from djoser.views import UserViewSet

from .filters import RecipeFilter
from .paginations import ApiPagination
from .permissions import (
    IsAuthorOrAdminOrReadOnlyPermission,
    IsCurrentUserOrAdminOrReadOnlyPermission
)
from .serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    RecipeSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagSerializer
)
from .utils import shopping_cart_ingredients
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Favorite,
    ShoppingCart
)
from users.models import Subscribe


User = get_user_model()


SUBSCRIBE_ERROR = 'Объект не найден!'
SUBSCRIBE_ERROR_VALIDATION = (
    'Ошибка валидации!\n'
    'Данные, поступившие в POST-запросе не прошли валидацию!\n'
    'Поступившие данные: {data}'
)

RECIPE_NOT_FOUND = 'Рецепт с id={id} не найден!'

FAVORITE_ADD_ERROR = (
    'Рецепт {recipe} уже находится в избранных у пользователя {user}!'
)
FAVORITE_NOT_FOUND = (
    'Рецепт {recipe} не найден среди избранных пользователя {user}!'
)

SHOPPING_CART_ADD_ERROR = (
    'Рецепт {recipe} уже находится в списке покупок пользователя {user}!'
)
SHOPPING_CART_NOT_FOUND = (
    'Рецепт {recipe} не найден списках покупок пользователя {user}!'
)
SHOPPING_CART_NONE = (
    'Список покупок пользователя {user} пуст!'
)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsCurrentUserOrAdminOrReadOnlyPermission,)
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
                SUBSCRIBE_ERROR_VALIDATION.format(data=request.data),
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscribe.objects.filter(author=author, user=user).exists():
            Subscribe.objects.get(author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
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


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnlyPermission,)
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
            self.add_pecipe_to_user(
                self,
                request,
                Favorite,
                FavoriteSerializer,
                *args,
                **kwargs
            )
        else:
            self.delete_recipe_from_user(
                self,
                request,
                Favorite,
                *args,
                **kwargs
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
            self.add_pecipe_to_user(
                self,
                request,
                ShoppingCart,
                ShoppingCartSerializer,
                *args,
                **kwargs
            )
        else:
            self.delete_recipe_from_user(
                self,
                request,
                ShoppingCart,
                *args,
                **kwargs
            )

    def add_pecipe_to_user(self,
                           request,
                           model,
                           serializer,
                           *args,
                           **kwargs):
        """
        Функция добавления записи в промежуточную таблицу
        для переданной модели.
        """
        user = request.user
        if not model.objects.filter(id=self.kwargs.get('pk')).exists():
            return Response(
                {'errors': RECIPE_NOT_FOUND.format(
                    id=kwargs.get('pk')
                )},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': FAVORITE_ADD_ERROR.format(
                    recipe=recipe.name,
                    user=user.username
                )},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

    def delete_recipe_from_user(self,
                                request,
                                model,
                                *args,
                                **kwargs):
        """
        Функция удаления записи из промежуточной таблицы
        для переданной модели.
        """
        user = request.user
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        if not model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': SHOPPING_CART_NOT_FOUND.format(
                    recipe=recipe.name,
                    user=user.username
                )},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        """Функция скачивания списка покупок."""
        user = User.objects.get(id=request.user.pk)
        if user.shopping_cart.exists():
            return shopping_cart_ingredients(self, request)
        return Response(
            SHOPPING_CART_NONE.format(
                user=user.username
            ),
            status=status.HTTP_404_NOT_FOUND
        )
