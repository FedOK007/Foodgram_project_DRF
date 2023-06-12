import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recieps.models import Ingredient, Tag
from recieps.models import Reciep, ReciepToIngredient

from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ReciepClassicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reciep
        fields = ('id', 'name', 'image', 'cooking_time', )
        read_only_fields = ('id', 'name', 'image', 'cooking_time', )


class FavoriteSerializer(ReciepClassicSerializer):
    pass


class ReciepShoppingcartSerializer(ReciepClassicSerializer):
    pass


class ReciepToIngredientSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field='id',
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
        source='ingredient'
    )
    measurement_unit = serializers.SlugRelatedField(
        read_only=True,
        slug_field='measurement_unit',
        source='ingredient'
    )

    class Meta:
        model = ReciepToIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name', 'measurement_unit')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class ReciepSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    tags = TagSerializer(required=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(many=False, read_only=True)
    # ingredients = serializers.SerializerMethodField()
    ingredients = ReciepToIngredientSerializer(
        many=True,
        source='reciep_ingridients'
    )

    class Meta:
        model = Reciep
        fields = ('id', 'author', 'tags', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart', )
        read_only_fields = ('id', 'author', 'is_favorited',
                            'is_in_shopping_cart', )

    # def get_ingredients(self, obj):
    #     return ReciepToIngredientSerializer(obj.reciep_ingridients.all(), many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return user.favorites.filter(reciep=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return user.shoppingcarts.filter(reciep=obj).exists()


class ReciepWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = ReciepToIngredientSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Reciep
        fields = ('tags', 'ingredients', 'image',
                  'name', 'text', 'cooking_time', )
        read_only_fields = ('author',)

    def create_ingredients(self, ingredients, reciep):
        for i in range(len(ingredients)):
            ingredients[i]['reciep'] = reciep
            ingredients[i] = ReciepToIngredient(**ingredients[i])
        ReciepToIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        reciep = Reciep.objects.create(**validated_data)
        reciep.tags.set(tags) # clear related data in tags and set a new
        self.create_ingredients(ingredients, reciep)
        return reciep

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        # for key, value in validated_data.items():
        #     setattr(instance, key, value)
        # instance.save()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)

        return instance

    def to_representation(self, instance):
        return ReciepSerializer(instance, context=self.context).data

