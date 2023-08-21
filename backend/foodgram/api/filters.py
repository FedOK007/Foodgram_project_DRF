from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe, Ingredient, Tag


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def _filter_universal(self, queryset, value, filter_parameters):
        if value and self.request.user.is_authenticated:
            return queryset.filter(**filter_parameters)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        filter_parameters = {'favorite_recipe__user': self.request.user}
        return self._filter_universal(queryset, value, filter_parameters)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        filter_parameters = {'shoppingcarts_recipe__user': self.request.user}
        return self._filter_universal(queryset, value, filter_parameters)

    # def filter_tags(self, queryset, name, value):
    #     return queryset.filter(tags__slug__in=value).distinct()

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags')


class IngrigientFilter(FilterSet):
    name = filters.CharFilter(method='filter_name')

    def filter_name(self, queryset, name, value):
        return queryset.filter(name__istartswith=value)

    class Meta:
        model = Ingredient
        fields = ('name', )
