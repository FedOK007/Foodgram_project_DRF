from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from api.filters import RecipeFilter, IngrigientFilter
from api.permissions import IsAuthor
from api.serializers import FavoriteSerializer, IngredientSerializer
from api.serializers import RecipeSerializer, RecipeWriteSerializer
from api.serializers import RecipeShoppingcartSerializer, TagSerializer
from api.utils import generatePDF


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None


class IngredientVieWSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filter_class = IngrigientFilter


class RecipeViewSet(viewsets.ModelViewSet):
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

    @action(
        detail=True,
        methods=['POST', 'DELETE', ],
        url_path='favorite',
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk=None):
        instance = Recipe.objects.get(id=pk)
        favorite = instance.favorite_recipe.filter(user=request.user).first()
        if request.method == 'POST':
            if favorite:
                return Response(
                    {'errors': 'Recipes is already in favorites'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoriteSerializer(instance=instance)
            Favorite.objects.create(
                user=request.user,
                recipe=instance
            )
            return Response(serializer.data)

        if not favorite:
            return Response(
                {'errors': 'Recipes in favorites does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE', ],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk=None):
        instance = Recipe.objects.get(id=pk)
        shopping_cart = instance.shoppingcarts_recipe.filter(user=request.user).first()
        if request.method == 'POST':
            if shopping_cart:
                return Response(
                    {'errors': 'Recipes is already in shopping cart'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeShoppingcartSerializer(instance=instance)
            ShoppingCart.objects.create(
                user=request.user,
                recipe=instance
            )
            return Response(serializer.data)
        if not shopping_cart:
            return Response(
                {'errors': 'Recipes in shopping cart does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def GeneratePDFApi(request):
    return generatePDF(request)
