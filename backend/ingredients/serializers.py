from rest_framework.serializers import ModelSerializer

from .models import Ingredient


class IngredientSerializer(ModelSerializer):
    """Сериализатора для модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__'
