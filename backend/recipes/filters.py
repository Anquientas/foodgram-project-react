from django.contrib import admin
from django.db.models import Min, Max

from .models import Recipe


class CookingTimeFilter(admin.SimpleListFilter):
    """Фильтр для рецептов по времени приготоления."""

    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    @staticmethod
    def calculate_parameters():
        time_min = int(Recipe.objects.aggregate(
            time_min=Min('cooking_time')
        )['time_min'])
        if not time_min:
            return False, None
        time_max = int(Recipe.objects.aggregate(
            time_max=Max('cooking_time')
        )['time_max'])
        if time_min == time_max:
            return False, None
        time_range_min = int((time_max + 2 * time_min) / 3)
        time_range_max = int((2 * time_max + time_min) / 3)
        return ([time_min, time_range_min, time_range_max, time_max], [
            Recipe.objects.filter(
                cooking_time__lte=time_range_min
            ).count(),
            Recipe.objects.filter(
                cooking_time__lte=time_range_max,
                cooking_time__gt=time_range_min
            ).count(),
            Recipe.objects.filter(
                cooking_time__gt=time_range_max
            ).count()
        ])

    def lookups(self, request, model_admin):
        times, counts = self.calculate_parameters()
        if not times:
            return None
        return (
            (str(times[0]) + ',' + str(times[1]),
             'Быстрые, менее {time} мин ({count})'.format(
                time=times[1],
                count=counts[0]
            )),
            (str(times[1]) + ',' + str(times[2]),
             'Средние, до {time} мин ({count})'.format(
                time=times[2],
                count=counts[1]
            )),
            (str(times[2]) + ',' + str(times[3]),
             'Долгие, более {time} мин ({count})'.format(
                time=times[2],
                count=counts[2]
            )),
        )

    def queryset(self, request, queryset):
        if self.value():
            range_values = self.value().split(',')
            return queryset.filter(
                cooking_time__gt=int(range_values[0]),
                cooking_time__lte=int(range_values[1])
            )
        return queryset
