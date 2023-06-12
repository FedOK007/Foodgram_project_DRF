from django.conf import settings
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from recieps.models import Favorite, Ingredient, Reciep, Tag, ShoppingCart
from api.permissions import IsAuthor
from api.serializers import FavoriteSerializer
from api.serializers import IngredientSerializer, ReciepSerializer, ReciepWriteSerializer
from api.serializers import TagSerializer, ReciepShoppingcartSerializer
from api.serializers import ReciepToIngredientSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None


class IngrigientFilter(FilterSet):
    name = filters.CharFilter(method='filter_name')

    def filter_name(selg, queryset, name, value):
        return queryset.filter(name__istartswith=value)

    class Meta:
        model = Ingredient
        fields = ('name', )


class IngredientVieWSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filter_class = IngrigientFilter


class ReciepFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')
    # for filter AND (bug in initial docs)
    # tags = filters.CharFilter(field_name='tags__slug', method='filter_tags')

    # filter OR style
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug', method='filter_tags')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_reciep__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcarts_reciep__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, name, value):
        # for filter AND (bug in initial docs)
        # return queryset.filter(tags__slug=value).distinct()

        # filter OR style
        return queryset.filter(tags__slug__in=value).distinct()

    class Meta:
        model = Reciep
        fields = ('author', 'is_favorited', 'is_in_shopping_cart', 'tags')


class ReciepViewSet(viewsets.ModelViewSet):
    queryset = Reciep.objects.select_related('author').all().order_by('-id')
    serializer_class = ReciepSerializer
    permission_classes = [AllowAny, ]
    # ilter_backends = (DjangoFilterBackend, )
    # filterset_class = ReciepFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', ]:
            return ReciepWriteSerializer
        return ReciepSerializer

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
        instance = Reciep.objects.get(id=pk)
        favorite = instance.favorite_reciep.filter(user=request.user).first()
        if request.method == 'POST':
            if favorite:
                return Response(
                    {'errors': 'Recieps is already in favorites'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoriteSerializer(instance=instance)
            Favorite.objects.create(
                user=request.user,
                reciep=instance
            )
            return Response(serializer.data)

        if request.method == 'DELETE':
            if not favorite:
                return Response(
                    {'errors': 'Recieps in favorites does not exist'},
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
        instance = Reciep.objects.get(id=pk)
        shopping_cart = instance.shoppingcarts_reciep.filter(user=request.user).first()
        if request.method == 'POST':
            if shopping_cart:
                return Response(
                    {'errors': 'Recieps is already in shopping cart'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = ReciepShoppingcartSerializer(instance=instance)
            ShoppingCart.objects.create(
                user=request.user,
                reciep=instance
            )
            return Response(serializer.data)
        if request.method == 'DELETE':
            if not shopping_cart:
                return Response(
                    {'errors': 'Recieps in shopping cart does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

from django.shortcuts import render
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from rest_framework.decorators import api_view, permission_classes
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab import rl_config


def get_ingredients_for_pfd(request):
    user = request.user
    recieps = Reciep.objects.filter(shoppingcarts_reciep__user=request.user)
    context = {'request': request}
    serialiser = ReciepSerializer(instance=recieps, many=True, context=context)

    ingredient_list = {}
    for reciep in serialiser.data:
        for ingredient in reciep['ingredients']:
            name = ingredient['name']
            amount = ingredient['amount']
            measurement_unit = ingredient['measurement_unit']
            if name in ingredient_list:
                ingredient_list[name][0] += amount
            else:
                ingredient_list[name] = [amount, measurement_unit]
    shopping_list = []
    for key, value in ingredient_list.items():
        shopping_list.append(f'{key} ({value[1]}) - {value[0]}')
    # text = '\n'.join(shopping_list)
    return shopping_list


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def generatePDF(request):
    rl_config.TTFSearchPath.append(str(settings.PDF_FONTS_DIR))
    shopping_list = get_ingredients_for_pfd(request)
    buffer = io.BytesIO()
    PDF_FORNT = settings.PDF_FONTS_FILE
    page = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont(PDF_FORNT.split('.')[0], 'Arial.ttf'))
    page.setFont('Arial', 12)
    y_coordinate = 800
    page.drawString(200, y_coordinate, "Список покупок:")
    for item in shopping_list:
        y_coordinate -=20
        page.drawString(100, y_coordinate, item)    
    page.showPage()
    page.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='attempt1.pdf')
