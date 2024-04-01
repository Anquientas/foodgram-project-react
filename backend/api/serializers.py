from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as UserSerializerBase
from drf_extra_fields.fields import Base64ImageField
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    CurrentUserDefault,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField
)

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Subscribe,
    Tag
)


User = get_user_model()


INGREDIENTS_NEED = 'Необходимо добавить хотя бы один продукт!'
INGREDIENT_REPEAT = 'Продукты {elements} повторяется!'
INGREDIENT_AMOUNT = (
    'Мера продукта {ingredient} должна быть не менее 1. Сейчас - {amount}!'
)

TAGS_NEED = 'Необходимо добавить хотя бы один тег!'
TAG_REPEAT = 'Теги {elements} повторяются!'

IS_SUBSCRIBED_IS_TRUE = (
    'Пользователь {user} уже подписан на пользователя {author}!'
)
IS_SUBSCRIBED_IS_FALSE = (
    'Пользователь {user} не подписан на пользователя {author}!'
)
IS_SUBSCRIBED_FOR_NO_AUTHOR = (
    'Пользователь {user} не может подписываться на самого себя!'
)
IMAGE_IS_REQUIRED = 'Изображение обязательно!'


class UserSerializer(UserSerializerBase):
    """Сериализатор для модели пользователя."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            *UserSerializerBase.Meta.fields,
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (
            not user.is_anonymous and Subscribe.objects.filter(
                user=user,
                author=author
            ).exists()
        )


class SubscribeReadSerializer(UserSerializer):
    """Сериализатор для чтения подписки."""

    recipes = SerializerMethodField()
    recipes_count = IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('__all__',)

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = int(request.GET.get('recipes_limit', 10**10))
        return RecipeSubscribeSerializer(
            author.recipes.all()[:limit],
            many=True,
            context={'request': request}
        ).data


class SubscribeSerializer(ModelSerializer):
    """Сериализатор для создания и удаления подписки."""

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        request = self.context.get('request')
        author = data.get('author')
        user = request.user
        if user == author:
            raise ValidationError(
                detail=IS_SUBSCRIBED_FOR_NO_AUTHOR.format(
                    user=user.username
                ),
                code=status.HTTP_400_BAD_REQUEST
            )
        if Subscribe.objects.filter(author=author, user=user).exists():
            if request.method == 'POST':
                raise ValidationError(
                    detail=IS_SUBSCRIBED_IS_TRUE.format(
                        user=user.username,
                        author=author.username
                    ),
                    code=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DEL':
            raise ValidationError(
                detail=IS_SUBSCRIBED_IS_FALSE.format(
                    user=user.username,
                    author=author.username
                ),
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, subscribe):
        return SubscribeReadSerializer(
            subscribe.get('author'),
            context=self.context
        ).data


class TagSerializer(ModelSerializer):
    """Сериализатор для модели тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    """Сериализатора для модели продукта."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)


class IngredientRecipeSerializer(ModelSerializer):
    """
    Сериализатор для модели продукта для рецепта
    (связанной модели продукта и рецепта).
    """

    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


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


class RecipeSerializerBase(ModelSerializer):
    """Базовый сериализатор для модели рецепта."""

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
        read_only_fields = ('__all__',)

    def get_is_favorited(self, recipe):
        return (
            not self.context.get('request').user.is_anonymous
            and Favorite.objects.filter(recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        return (not self.context.get('request').user.is_anonymous
                and ShoppingCart.objects.filter(recipe=recipe).exists())


class RecipeReadSerializer(RecipeSerializerBase):
    """Сериализатор для модели рецепта при чтении данных."""
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredients_recipes'
    )


class RecipeSerializer(RecipeSerializerBase):
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
    image = Base64ImageField(required=True)
    author = UserSerializer(default=CurrentUserDefault())
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta(RecipeSerializerBase.Meta):
        read_only_fields = ('is_favorited', 'is_in_shopping_cart')

    @staticmethod
    def add_ingredients(ingredients, model):
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=model,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    @staticmethod
    def check_duplicate(check_list, message, key):
        elements_list_duplicate = [
            (element.name if not key else element.get(key).name)
            for element in check_list if check_list.count(element) > 1
        ]
        if elements_list_duplicate:
            raise ValidationError(
                {'field': message.format(
                    elements=set(elements_list_duplicate)
                )}
            )
        return check_list

    def validate_image(self, image):
        if image:
            return image
        raise ValidationError(IMAGE_IS_REQUIRED)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError({'ingredients': INGREDIENTS_NEED})
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
        ingredients = self.check_duplicate(
            ingredients,
            INGREDIENT_REPEAT,
            'id'
        )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise ValidationError({'tags': TAGS_NEED})
        tags = self.check_duplicate(tags, TAG_REPEAT, '')
        return tags

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if self.validate_ingredients(validated_data.get('ingredients')):
            ingredients = validated_data.pop('ingredients')
        if self.validate_tags(validated_data.get('tags')):
            tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.add_ingredients(ingredients, instance)
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class RecipeSubscribeSerializer(ModelSerializer):
    """
    Сериализатор для модели рецепта (Recipe)
    при выводе в списке рецептов в подписках списках избранного и покупок
    текущего пользователя.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteAndShoppingCartSerializerBase(ModelSerializer):
    """
    Базовый сериализатор
    для модели избранных рецептов пользователя (Favorite)
    и для модели списка покупок пользователя (ShoppingCart).
    """

    class Meta:
        fields = ('recipe',)

    def to_representation(self, instance):
        return RecipeSubscribeSerializer(
            instance,
            context=self.context
        ).data


class FavoriteSerializer(FavoriteAndShoppingCartSerializerBase):
    """Сериализатор для модели избранных рецептов пользователя (Favorite)."""

    class Meta(FavoriteAndShoppingCartSerializerBase.Meta):
        model = Favorite


class ShoppingCartSerializer(FavoriteAndShoppingCartSerializerBase):
    """Сериализатор для модели списка покупок пользователя (ShoppingCart)."""

    class Meta(FavoriteAndShoppingCartSerializerBase.Meta):
        model = ShoppingCart
