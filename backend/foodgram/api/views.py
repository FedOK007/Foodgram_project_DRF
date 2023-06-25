from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from api.filters import RecipeFilter, IngrigientFilter
from api.permissions import IsAuthor
from api.serializers import (
    FavoriteSerializer, IngredientSerializer,
    RecipeSerializer, RecipeWriteSerializer,
    RecipeShoppingcartSerializer, TagSerializer
)
from api.utils import generate_pdf


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None


class IngredientVieWSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filter_class = IngrigientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related('author').all().order_by('-id')
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny, ]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', ]:
            return RecipeWriteSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, ]
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthor, ]
        return super().get_permissions()

    def _extra_action_methods_universal(self, name, request, pk=None):
        instance = Recipe.objects.get(id=pk)
        available_actions = {
            'favorite': {
                'related_model': instance.favorite_recipe,
                'model': Favorite,
                'serialiser_class': FavoriteSerializer,
            },
            'shopping_cart': {
                'related_model': instance.shoppingcarts_recipe,
                'model': ShoppingCart,
                'serialiser_class': RecipeShoppingcartSerializer,
            }
        }

        if name not in available_actions:
            return Response(
                {'errors': 'Bad request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        related_models = available_actions[name]['related_model']
        serializer_class = available_actions[name]['serialiser_class']
        model = available_actions[name]['model']

        related_object = related_models.filter(user=request.user).first()

        if request.method == 'POST':
            if related_object:
                return Response(
                    {'errors': f'Recipes is already in {name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = serializer_class(instance=instance)
            model.objects.create(
                user=request.user,
                recipe=instance
            )
            return Response(serializer.data)

        if not related_object:
            return Response(
                {'errors': f'Recipes in {name} does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        related_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE', ],
        url_path='favorite',
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk=None):
        return self._extra_action_methods_universal('favorite', request, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE', ],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk=None):
        return self._extra_action_methods_universal(
            'shopping_cart',
            request,
            pk
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def generate_pdf_api(request):
    return generate_pdf(request)
