from django.contrib import admin

from .models import (
    Subscribe,
    User
)


class UserAdmin(admin.ModelAdmin):
    """Админ-зона для пользователей."""
    list_display = (
        'id',
        'username',
        'email',
        'password',
        'first_name',
        'last_name'
    )
    list_editable = (
        'username',
        'email',
        'password',
        'first_name',
        'last_name'
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_filter = (
        'username',
        'email',
        'first_name',
        'last_name'
    )


class SubscribeAdmin(admin.ModelAdmin):
    """Админ-зона для подписок."""
    list_display = ('author', 'user')
    list_filter = ('author', 'user')
    search_fields = ('author', 'user')


admin.site.empty_value_display = 'Не задано'
admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
