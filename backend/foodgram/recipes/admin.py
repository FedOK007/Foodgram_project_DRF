from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from recipes.models import (
    Tag, Recipe, Ingredient, RecipeToIngredient, RecipeToTag, ShoppingCart
)


class CheckRequiredFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        correct_ingredient_list = False
        for form in self.forms:
            if not form.is_valid():
                return
            if not form.cleaned_data:
                raise ValidationError('This field is required.')
            if not form.cleaned_data.get('DELETE'):
                correct_ingredient_list = True
        if not correct_ingredient_list:
            raise ValidationError('This field could not be empty.')


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'color', 'slug'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeToTagAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'tag'
    )


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeToIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
    empty_value_display = '-пусто-'


class RecipeToIngredientInline(admin.TabularInline):
    model = RecipeToIngredient
    extra = 0
    formset = CheckRequiredFormSet


class RecipeToTagsInline(admin.TabularInline):
    model = RecipeToTag
    extra = 0
    formset = CheckRequiredFormSet


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image', 'text', )
    inlines = [
        RecipeToTagsInline,
        RecipeToIngredientInline,
        ShoppingCartInline,
    ]
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngridientAdmin)
admin.site.register(RecipeToIngredient, RecipeToIngredientAdmin)
admin.site.register(RecipeToTag, RecipeToTagAdmin)
