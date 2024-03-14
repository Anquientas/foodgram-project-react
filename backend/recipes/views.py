from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import AllowAny, SAFE_METHODS


from .models import Recipe
from .serializers import RecipeSerializer, RecipeGetSerializer


class RecipeViewSet(ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = ...  # Author, Admin or ReadOnly
    http_method_names = ('get', 'head', 'options', 'patch', 'post', 'delete')

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeSerializer

