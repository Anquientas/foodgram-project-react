from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny


from .models import Tag
from .serializers import TagSerializer


class TagViewSet(ListModelMixin,
                 RetrieveModelMixin,
                #  ReadOnlyModelViewSet,
                 GenericViewSet,):
    """Вьюсет для модели тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
