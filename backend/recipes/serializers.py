import base64

from django.core.files.base import ContentFile
from rest_framework.serializers import (
    ModelSerializer,
    # PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField,
    ImageField
)
from rest_framework.validators import ValidationError

from .models import (
    Recipe,
    IngredientRecipe,
    Favorite,
    ShoppingCart,
    Tag,
    Ingredient
)
# from users.serializers import UserSerializer


TAGS_NEED = 'Необходимо выбрать тег!'
TAGS_REPEAT = 'Необходимо устранить повтор тегов! Повторяющиеся теги: {tags}'


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """Сериализатор для модели тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Сериализатора для модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__'


class IngredientRecipeSerializer(ModelSerializer):
    """
    Сериализатор для модели ингредиента для рецепта
    (связанной модели ингредиента и рецепта).
    """

    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(ModelSerializer):
    """Сериализатор для модели рецепта при чтении данных."""
    # author = UserSerializer()
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True
    )
    is_favorite = SerializerMethodField(),
    is_in_shopping_cart = SerializerMethodField(),

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = '__all__'

    def get_is_favorite(self, recipe):
        # Если работает - свернуть
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(recipe=recipe).exist()
        return False

    def get_is_in_shopping_cart(self, recipe):
        # Если работает - свернуть
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=recipe).exist()
        return False


class RecipeSerializer(ModelSerializer):
    """Сериализатор для модели рецепта при редактировании данных."""

    # author = UserSerializer()
    tags = TagSerializer(
        many=True,
    )
    ingredients = IngredientRecipeSerializer(
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            # 'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError(
                {'tags': TAGS_NEED}
            )
        tags_list = set()
        for tag in tags:
            if tags.count(tag) > 1:
                tags_list.add(tag)
        if tags_list:
            raise ValidationError(
                {'tags': TAGS_REPEAT.format(tags=tags_list)}
            )
        return tags
