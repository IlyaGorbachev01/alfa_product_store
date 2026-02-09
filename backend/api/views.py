from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.permissions import IsOwner
from api.serializers import (
    CartItemDetailSerializer,
    CartItemSerializer,
    CartSummarySerializer,
    CategorySerializer,
    ProductSerializer,
)
from shop.models import CartItem, Category, Product


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра категорий с подкатегориями."""

    queryset = Category.objects.prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def list(self, request: Request, *args, **kwargs) -> Response:
        """Получение списка всех категорий с вложенными подкатегориями."""
        cache_key = 'categories_with_subcategories'
        cached_data = cache.get(cache_key)

        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, timeout=settings.CACHE_TIMEOUT)
            return response

        return Response(cached_data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра продуктов."""

    queryset = Product.objects.select_related(
        'subcategory', 'subcategory__category'
    )
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self) -> QuerySet:
        """Фильтрация продуктов по категории и подкатегории."""
        queryset: QuerySet = super().get_queryset()
        category_slug = self.request.query_params.get('category', None)
        subcategory_slug = self.request.query_params.get('subcategory', None)

        if category_slug:
            queryset = queryset.filter(
                subcategory__category__slug=category_slug
            )
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)

        return queryset


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet для операций с корзиной."""

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self) -> QuerySet:
        """Получение элементов корзины текущего пользователя."""
        return CartItem.objects.filter(user=self.request.user).select_related(
            'product'
        )

    def get_serializer_class(
        self,
    ) -> type[
        CartItemSerializer | CartItemDetailSerializer | CartSummarySerializer
    ]:
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'list':
            return CartItemDetailSerializer
        elif self.action in ['summary', 'clear_cart']:
            return CartSummarySerializer
        return CartItemSerializer

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request: Request) -> Response:
        """Получение итоговой информации о корзине."""
        cart_items: QuerySet = self.get_queryset()
        total_items: int = sum(item.quantity for item in cart_items)
        total_price: Decimal = sum(item.total_price for item in cart_items)

        data: dict = {
            'items': CartItemDetailSerializer(
                cart_items, many=True, context={'request': request}
            ).data,
            'total_items': total_items,
            'total_price': total_price,
        }
        return Response(data)

    @action(detail=False, methods=['post'], url_path='clear')
    def clear_cart(self, request: Request) -> Response:
        """Очистка всей корзины."""
        self.get_queryset().delete()
        return Response(
            {'detail': 'Корзина очищена'}, status=status.HTTP_204_NO_CONTENT
        )
