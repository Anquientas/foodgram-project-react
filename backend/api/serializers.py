from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    ModelSerializer,
    ReadOnlyField,
    SerializerMethodField,
    PrimaryKeyRelatedField,
    ImageField,
    IntegerField,
    CurrentUserDefault
)

from .fields import Base64ImageField
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    IngredientRecipe,
    Favorite,
    ShoppingCart
)
from users.models import Subscribe


User = get_user_model()


INGREDIENTS_NEED = 'Необходимо добавить хотя бы один ингредиент!'
INGREDIENT_REPEAT = 'Ингредиент {ingredient} повторяется!'
INGREDIENT_AMOUNT = (
    'Количество единиц измерения ингредиента {ingredient} '
    'должно быть не менее 1. Сейчас - {amount}!'
)

TAGS_NEED = 'Необходимо добавить хотя бы один тег!'
TAG_REPEAT = 'Ингредиент {tag} повторяется!'

IS_SUBSCRIBED_IS_TRUE = (
    'Пользователь {user} уже подписан на пользователя {author}!'
)
IS_SUBSCRIBED_IS_FALSE = (
    'Пользователь {user} не подписан на пользователя {author}!'
)
IS_SUBSCRIBED_FOR_NO_AUTHOR = (
    'Пользователь {user} не может подписываться на самого себя!'
)


class CustomUserSerializer(ModelSerializer):
    """Сериализатор для модели пользователя."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscribe.objects.filter(
                user=user,
                author=author
            ).exists()
        return False


class SubscribeSerializer(ModelSerializer):
    """Сериализатор для модели подписки."""

    email = ReadOnlyField(source='author.email')
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, subscribe):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscribe.objects.filter(
                author=subscribe.author,
                user=user
            ).exists()
        return False

    def get_recipes(self, subscribe):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=subscribe.author)
        limit = request.GET.get('recipes_limit')
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeSubscribeSerializer(recipes, many=True).data

    def get_recipes_count(self, subscribe):
        return Recipe.objects.filter(author=subscribe.author).count()

    def validate(self, data):
        request = self.context.get('request')
        author = self.context.get('author')
        user = request.user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail=IS_SUBSCRIBED_IS_TRUE.format(
                    user=user.username,
                    author=author.username
                ),
                code=status.HTTP_400_BAD_REQUEST
            )
        if (
            request.method == 'DEL'
            and not Subscribe.objects.filter(
                author=author,
                user=user
            ).exists()
        ):
            raise ValidationError(
                detail=IS_SUBSCRIBED_IS_FALSE.format(
                    user=user.username,
                    author=author.username
                ),
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail=IS_SUBSCRIBED_FOR_NO_AUTHOR.format(
                    user=user.username
                ),
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


class TagSerializer(ModelSerializer):
    """Сериализатор для модели тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    """Сериализатора для модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)


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


class RecipeReadSerializer(ModelSerializer):
    """Сериализатор для модели рецепта при чтении данных."""
    author = CustomUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('__all__',)

    def get_is_favorited(self, recipe):
        if not self.context.get('request').user.is_anonymous:
            return Favorite.objects.filter(recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        if not self.context.get('request').user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=recipe).exists()
        return False


class AddIngredientInRecipeSerializer(ModelSerializer):
    """
    Сериализатор для поля "ingredient" модели рецепта (Recipe)
    при создании рецепта.
    """
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(ModelSerializer):
    """
    Сериализатор для модели рецепта (Recipe)
    при создании и редактировании данных.
    """

    ingredients = AddIngredientInRecipeSerializer(
        many=True,
        write_only=True
    )
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = CustomUserSerializer(default=CurrentUserDefault())
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError({'ingredients': INGREDIENTS_NEED})
        ingredients_list = []
        for unit_ingredient in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=unit_ingredient['id'].id
            )
            amount = int(unit_ingredient['amount'])
            if amount < 1:
                raise ValidationError(
                    {'ingredients': INGREDIENT_AMOUNT.format(
                        ingredient=ingredient.name,
                        amount=amount
                    )}
                )
            if ingredient in ingredients_list:
                raise ValidationError(
                    {'ingredients': INGREDIENT_REPEAT.format(
                        ingredient=ingredient.name
                    )}
                )
            ingredients_list.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError({'tags': TAGS_NEED})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {'tags': TAG_REPEAT.format(tag=tag.name)}
                )
            tags_list.append(tag)
        return tags

    def to_representation(self, instance):
        ingredients = super().to_representation(instance)
        ingredients['ingredients'] = IngredientRecipeSerializer(
            instance.recipe_ingredients.all(),
            many=True
        ).data
        ingredients['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        return ingredients

    def add_tags(self, tags, model):
        model.tags.set(tags)

    def add_ingredients(self, ingredients, model):
        for ingredient in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=model,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.add_ingredients(ingredients, recipe)
        self.add_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        if self.validate_ingredients(validated_data.get('ingredients')):
            ingredients = validated_data.pop('ingredients')
        if self.validate_tags(validated_data.get('tags')):
            tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.add_ingredients(ingredients, instance)
        self.add_tags(tags, instance)
        return super().update(instance, validated_data)

    def get_is_favorited(self, recipe):
        if not self.context.get('request').user.is_anonymous:
            return Favorite.objects.filter(recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        if not self.context.get('request').user.is_anonymous:
            return ShoppingCart.objects.filter(recipe=recipe).exists()
        return False


class FavoriteSerializer(ModelSerializer):
    """Сериализатор для модели избранных рецептов пользователя (Favorite)."""

    id = PrimaryKeyRelatedField(
        source='recipe.id',
        read_only=True
    )
    name = ReadOnlyField(
        source='recipe.name',
        read_only=True
    )
    image = ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(ModelSerializer):
    """Сериализатор для модели списка покупок пользователя (ShoppingCart)."""

    id = PrimaryKeyRelatedField(
        source='recipe.id',
        read_only=True
    )
    name = ReadOnlyField(
        source='recipe.name',
        read_only=True
    )
    image = ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSubscribeSerializer(ModelSerializer):
    """
    Сериализатор для модели рецепта (Recipe)
    при выводе в списке рецептов в подписках текущего пользователя.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)
