from django.contrib import admin


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        return (
            ('quick', 'Быстрее 30 мин'),
            ('medium', 'За час успеем'),
            ('long', 'Долгие'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'quick':
            return queryset.filter(cooking_time__lte=30)
        elif self.value() == 'medium':
            return queryset.filter(cooking_time__lte=60, cooking_time__gt=30)
        elif self.value() == 'long':
            return queryset.filter(cooking_time__gt=60)
