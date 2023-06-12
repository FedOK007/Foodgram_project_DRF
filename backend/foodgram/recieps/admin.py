from django.contrib import admin
from django.contrib.auth import get_user_model

from recieps.models import Tag, Reciep, Ingredient, ReciepToIngredient, ReciepToTag, ShoppingCart


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'color', 'slug'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class ReciepToTagAdmin(admin.ModelAdmin):
    list_display = (
        'reciep',
        'tag'
    )


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class ReciepToIngredientAdmin(admin.ModelAdmin):
    list_display = ('reciep', 'ingredient', 'amount',)
    empty_value_display = '-пусто-'


class ReciepToIngredientInline(admin.TabularInline):
    model = ReciepToIngredient
    extra = 1


class ReciepToTagsInline(admin.TabularInline):
    model = ReciepToTag
    extra = 1


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    extra = 1


class ReciepAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image', 'text', )
    inlines = [ReciepToTagsInline, ReciepToIngredientInline, ShoppingCartInline, ]
    empty_value_display = '-пусто-'


admin.site.register(Reciep, ReciepAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngridientAdmin)
admin.site.register(ReciepToIngredient, ReciepToIngredientAdmin)
admin.site.register(ReciepToTag, ReciepToTagAdmin)
