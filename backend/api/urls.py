from django.urls import include, path
from rest_framework.routers import SimpleRouter

# from .views import (
#     ...
# )
from recipes.views import IngredientViewSet
from recipes.views import TagViewSet


router_v1 = SimpleRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
# router_v1.register('recipes', ..., basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
# router_v1.register('users', ..., basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    # path('v1/auth/', include('djoser.urls')),
    path('v1/auth/', include('djoser.urls.authtoken')),
]
