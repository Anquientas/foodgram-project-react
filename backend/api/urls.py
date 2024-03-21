from django.urls import include, path
from rest_framework.routers import SimpleRouter

from recipes.views import IngredientViewSet
from recipes.views import TagViewSet
from recipes.views import RecipeViewSet
from users.views import CustomUserViewSet


router_v1 = SimpleRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
