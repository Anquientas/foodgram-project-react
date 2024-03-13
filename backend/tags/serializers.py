from rest_framework import serializers

from .models import Tag


class TagSerializers(serializers.ModelSerializer):
    """Сериализатор для модели тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__'
