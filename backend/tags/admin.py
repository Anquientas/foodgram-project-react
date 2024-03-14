from django.contrib import admin

from .models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    list_editable = ('name', 'slug', 'color')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug', 'color')
    list_display_links = ('id', 'name')


admin.site.empty_value_display = 'Не задано'
admin.site.register(Tag, TagAdmin)
