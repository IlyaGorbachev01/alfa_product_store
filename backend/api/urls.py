from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import CartViewSet, CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', obtain_auth_token, name='token_obtain'),
]
