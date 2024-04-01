from ast import literal_eval

from django.contrib import admin

from .models import Recipe


class CookingTimeFilter(admin.SimpleListFilter):
    """Фильтр для рецептов по времени приготовления."""

    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    @staticmethod
    def calculate_parameters():
        times = set(recipe.cooking_time for recipe in Recipe.objects.all())
        bot, top = min(times), max(times)
        if bot == top:
            return False, None
        time_min = int((top + 2 * bot) / 3)
        time_max = int((2 * top + bot) / 3)
        counts = [0, 0, 0]
        for time in times:
            if time < time_min:
                counts[0] += 1
            elif time < time_max:
                counts[1] += 1
            else:
                counts[2] += 1
        return ([0, time_min, time_max, 10 ** 10], counts)

    def lookups(self, request, model_admin):
        times, counts = self.calculate_parameters()
        if not times:
            return None
        return (
            (times[:2], f'Быстрые, менее {times[1]} мин ({counts[0]})'),
            (times[1:3], f'Средние, до {times[2]} мин ({counts[1]})'),
            (times[2:], f'Долгие ({counts[2]})')
        )

    def queryset(self, request, recipes):
        if self.value():
            return recipes.filter(
                cooking_time__range=literal_eval(self.value()),
            )
        return recipes
