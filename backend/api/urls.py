from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    ...
)


router_v1 = SimpleRouter()
router_v1.register('ingredients', ..., basename='ingredients')
router_v1.register('recipes', ..., basename='recipes')
router_v1.register('tags', ..., basename='tags')
router_v1.register('users', ..., basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(auth_urls))
]




urlpatterns = [
    (...),
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.jwt')),
]
