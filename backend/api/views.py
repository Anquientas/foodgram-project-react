from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as UserViewSetBase
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
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

from .filters import RecipeFilter, IngredientFilter
from .paginations import ApiPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    SubscribeReadSerializer,
    TagSerializer,
    UserSerializer
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
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = UserSerializer
    pagination_class = ApiPagination

    def get_permissions(self):
        if self.request.method == 'GET' and self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, *args, **kwargs):
        """Функция создания и удаления подписки."""
        user = request.user
        id = self.kwargs.get('id')
        author = get_object_or_404(User, pk=int(id))
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'user': user.id, 'author': author.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(author=author, user=user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
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
        subscribes = User.objects.filter(authors__user=request.user)
        pages = self.paginate_queryset(subscribes)
        serializer = SubscribeReadSerializer(
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
        IsAuthorOrReadOnly,
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

    def add_or_delete_recipe_for_user(self, model, serializer, request, id):
        """
        Функция добавления записи в промежуточную таблицу или ее удаления,
        связанной с избранными рецептами и списком покупок
        для переданной модели текущего пользователя.
        """
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'POST':
            _, created = model.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if created:
                serializer = serializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            raise ValidationError(
                detail={'errors': ADD_ERROR.format(
                    recipe=recipe.name,
                    user=user.username
                )}
            )
        get_object_or_404(model, user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        return self.add_or_delete_recipe_for_user(
            Favorite,
            FavoriteSerializer,
            request,
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
        return self.add_or_delete_recipe_for_user(
            ShoppingCart,
            ShoppingCartSerializer,
            request,
            kwargs.get('pk')
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        """Функция скачивания списка покупок."""
        user = User.objects.get(id=request.user.pk)
        if user.shoppingcarts.exists():
            return FileResponse(
                shopping_cart_ingredients(request.user),
                as_attachment=True,
                filename=DOWNLOAD_FILENAME
            )
        raise NotFound(
            detail=SHOPPING_CART_NONE.format(
                user=user.username
            ),
        )
