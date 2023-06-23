from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import GeneratePDFApi
from api.views import IngredientVieWSet, RecipeViewSet, TagsViewSet
from users.views import SubscriptionUserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', SubscriptionUserViewSet, basename='users')
router_v1.register('tags', TagsViewSet, basename='tags')
router_v1.register('ingredients', IngredientVieWSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='pecieps')

urlpatterns = [
    path('recipes/download_shopping_cart/', GeneratePDFApi),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
