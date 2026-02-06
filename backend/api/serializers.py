"""Сериализаторы для API приложения магазина."""

from django.http import HttpRequest
from rest_framework import serializers

from api.constants import (
    MAX_TOTAL_PRICE_DIGITS,
    MIN_QUANTITY,
    TOTAL_PRICE_DECIMAL_PLACES,
)
from shop.constants import PRICE_DECIMAL_PLACES, PRICE_MAX_DIGITS
from shop.models import CartItem, Category, Product, SubCategory


class SubCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели SubCategory."""

    class Meta:
        """Метакласс для SubCategorySerializer."""

        model = SubCategory
        fields = ('id', 'name', 'slug', 'image')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category с вложенными подкатегориями."""

    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        """Метакласс для CategorySerializer."""

        model = Category
        fields = ('id', 'name', 'slug', 'image', 'subcategories')


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Product."""

    category = serializers.CharField(
        source='subcategory.category.name', read_only=True
    )
    subcategory = serializers.CharField(
        source='subcategory.name', read_only=True
    )
    price = serializers.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        read_only=True,
    )
    images = serializers.SerializerMethodField()

    class Meta:
        """Метакласс для ProductSerializer."""

        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'category',
            'subcategory',
            'price',
            'images',
        )

    def get_images(self, obj: Product) -> dict[str, str | None]:
        """Возвращает список URL изображений."""
        request: HttpRequest = self.context.get('request')
        return {
            'small': request.build_absolute_uri(obj.image_small.url)
            if obj.image_small
            else None,
            'medium': request.build_absolute_uri(obj.image_medium.url)
            if obj.image_medium
            else None,
            'large': request.build_absolute_uri(obj.image_large.url)
            if obj.image_large
            else None,
        }


class CartItemSerializer(serializers.ModelSerializer):
    """Сериализатор для операций с элементами корзины."""

    class Meta:
        """Метакласс для CartItemSerializer."""

        model = CartItem
        fields = ('id', 'product', 'quantity')

    def validate_quantity(self, value: int) -> int:
        """Проверка, что количество положительное."""
        if value < MIN_QUANTITY:
            raise serializers.ValidationError(
                f'Количество должно быть не менее {MIN_QUANTITY}'
            )
        return value


class CartItemDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального отображения элемента корзины."""

    product = ProductSerializer(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=MAX_TOTAL_PRICE_DIGITS,
        decimal_places=TOTAL_PRICE_DECIMAL_PLACES,
        read_only=True,
    )

    class Meta:
        """Метакласс для CartItemDetailSerializer."""

        model = CartItem
        fields = ('id', 'product', 'quantity', 'total_price', 'added_at')


class CartSummarySerializer(serializers.Serializer):
    """Сериализатор для итоговой информации о корзине."""

    items = CartItemDetailSerializer(many=True)
    total_items = serializers.IntegerField()
    total_price = serializers.DecimalField(
        max_digits=MAX_TOTAL_PRICE_DIGITS,
        decimal_places=TOTAL_PRICE_DECIMAL_PLACES,
    )
