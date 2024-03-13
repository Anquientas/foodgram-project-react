from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    ...
)
from tags.views import TagViewSet


router_v1 = SimpleRouter()
router_v1.register('ingredients', ..., basename='ingredients')
router_v1.register('recipes', ..., basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('users', ..., basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    # path('v1/auth/', include('djoser.urls')),
    path('v1/auth/', include('djoser.urls.authtoken')),
]
