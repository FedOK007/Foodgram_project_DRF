from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientVieWSet, ReciepViewSet, TagsViewSet
from users.views import SubscriptionUserViewSet
from api.views import generatePDF

router = DefaultRouter()
router.register('users', SubscriptionUserViewSet, basename='users')
# router.register(
#     r'users/(?P<user_id>\d+)/subscribe',
#     SubscriptionViewSet,
#     basename='subscribe'
# )
router_api = DefaultRouter()
router_api.register('tags', TagsViewSet, basename='tags')
router_api.register('ingredients', IngredientVieWSet, basename='ingredients')
router_api.register('recipes', ReciepViewSet, basename='pecieps')

urlpatterns = [
    #path(r'auth/users/<int:user_id>/subscribe/', SubscriptionViewSet.as_view()),
    path('recipes/download_shopping_cart/', generatePDF),
    path('', include(router.urls)),
    #path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_api.urls)),
    # path('shoppingcart/', DownloadShoppingCart.as_view())
]
