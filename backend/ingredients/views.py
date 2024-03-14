from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny

from .models import Ingredient
from serializers import IngredientSerializer


class IngredientViewSet(ListModelMixin,
                        RetrieveModelMixin,
                        # ReadOnlyModelViewSet,
                        GenericViewSet):
    """Вьюсет для модели ингредиента."""

    class Meta:
        model = Ingredient
        serializer_class = IngredientSerializer
        permission_classes = (AllowAny,)
