from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe, Ingredient


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')
    # for filter AND (bug in initial docs)
    # tags = filters.CharFilter(field_name='tags__slug', method='filter_tags')

    # filter OR style
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug', method='filter_tags')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcarts_recipe__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, name, value):
        # for filter AND (bug in initial docs)
        # return queryset.filter(tags__slug=value).distinct()

        # filter OR style
        return queryset.filter(tags__slug__in=value).distinct()

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags')


class IngrigientFilter(FilterSet):
    name = filters.CharFilter(method='filter_name')

    def filter_name(selg, queryset, name, value):
        return queryset.filter(name__istartswith=value)

    class Meta:
        model = Ingredient
        fields = ('name', )
