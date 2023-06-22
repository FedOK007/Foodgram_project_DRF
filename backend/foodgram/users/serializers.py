import base64

from django.contrib.auth import get_user_model
from djoser.conf import settings
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Subscriptions
from recipes.models import Recipe

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_subscribed', )
        read_only_fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_subscribed', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request:
            current_user = request.user
            if current_user != obj and current_user.is_authenticated:
                return Subscriptions.objects.filter(
                    subscriber=current_user,
                    subscription=obj
                ).exists()
        return False


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class FilterRecipesSerializer(serializers.ListSerializer):
    ''' customization ListSerializer (many=true) behaviour 
        more info https://www.django-rest-framework.org/api-guide/serializers/
    '''
    def to_representation(self, data):
        recipes_limit = self.context.get('request').query_params.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
        except (ValueError, TypeError):
            return super().to_representation(data)
        if recipes_limit > 0:
            data = data.all()[:recipes_limit]
        return super().to_representation(data)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        list_serializer_class = FilterRecipesSerializer
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionUserSerializer(UserSerializer):
    recipes = RecipeSerializer(many=True)
    is_subscribed = serializers.BooleanField(default=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()
