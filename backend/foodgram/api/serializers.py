from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeToIngredient, Tag
from users.serializers import CustomUserSerializer, Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeClassicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )
        read_only_fields = ('id', 'name', 'image', 'cooking_time', )


class FavoriteSerializer(RecipeClassicSerializer):
    pass


class RecipeShoppingcartSerializer(RecipeClassicSerializer):
    pass


class RecipeToIngredientSerializer(serializers.ModelSerializer):
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
        model = RecipeToIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)
    tags = TagSerializer(required=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(many=False, read_only=True)
    # ingredients = serializers.SerializerMethodField()
    ingredients = RecipeToIngredientSerializer(
        many=True,
        source='recipe_ingridients'
    )

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart', )
        read_only_fields = ('id', 'author', 'is_favorited',
                            'is_in_shopping_cart', )

    def _check_user(self):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return user

    def _check_existing_obj(self, name, filter_parameters):
        user = self._check_user()
        if not user:
            return False
        return getattr(user, name).filter(**filter_parameters).exists()

    def get_is_favorited(self, obj):
        name = 'favorites'
        filter_parameters = {'recipe': obj}
        return self._check_existing_obj(name, filter_parameters)

    def get_is_in_shopping_cart(self, obj):
        name = 'shoppingcarts'
        filter_parameters = {'recipe': obj}
        return self._check_existing_obj(name, filter_parameters)


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeToIngredientSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'image',
                  'name', 'text', 'cooking_time', )
        read_only_fields = ('author',)

    def create_ingredients(self, ingredients, recipe):
        for i in range(len(ingredients)):
            ingredients[i]['recipe'] = recipe
            ingredients[i] = RecipeToIngredient(**ingredients[i])
        RecipeToIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        # clear related data in tags and set a new
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        # alternatives
        # for key, value in validated_data.items():
        #     setattr(instance, key, value)
        # instance.save()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)

        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data
