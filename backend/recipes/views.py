# from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
# from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet
)
from rest_framework.permissions import AllowAny, SAFE_METHODS


from .models import (
    Recipe,
    Tag,
    Ingredient
)
from .serializers import (
    RecipeSerializer,
    RecipeGetSerializer,
    TagSerializer,
    IngredientSerializer
)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для модели ингредиента."""

    class Meta:
        model = Ingredient
        serializer_class = IngredientSerializer
        permission_classes = (AllowAny,)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = ...  # Author, Admin or ReadOnly
    http_method_names = ('get', 'head', 'options', 'patch', 'post', 'delete')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeSerializer
