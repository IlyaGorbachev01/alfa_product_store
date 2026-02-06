from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models

from .constants import (
    ADDED_AT_VERBOSE_NAME,
    CART_ITEM_VERBOSE_NAME,
    CART_ITEM_VERBOSE_NAME_PLURAL,
    CATEGORY_IMAGE_PATH,
    CATEGORY_VERBOSE_NAME,
    CATEGORY_VERBOSE_NAME_FIELD,
    CATEGORY_VERBOSE_NAME_PLURAL,
    CREATED_AT_VERBOSE_NAME,
    IMAGE_VERBOSE_NAME,
    LARGE_IMAGE_VERBOSE_NAME,
    MAX_NAME_LENGTH,
    MAX_SLUG_LENGTH,
    MEDIUM_IMAGE_VERBOSE_NAME,
    NAME_ORDERING,
    NAME_VERBOSE_NAME,
    PRICE_DECIMAL_PLACES,
    PRICE_MAX_DIGITS,
    PRICE_VERBOSE_NAME,
    PRODUCT_LARGE_IMAGE_PATH,
    PRODUCT_MEDIUM_IMAGE_PATH,
    PRODUCT_SMALL_IMAGE_PATH,
    PRODUCT_VERBOSE_NAME,
    PRODUCT_VERBOSE_NAME_PLURAL,
    QUANTITY_VERBOSE_NAME,
    SLUG_VERBOSE_NAME,
    SMALL_IMAGE_VERBOSE_NAME,
    SUBCATEGORY_IMAGE_PATH,
    SUBCATEGORY_VERBOSE_NAME,
    SUBCATEGORY_VERBOSE_NAME_FIELD,
    SUBCATEGORY_VERBOSE_NAME_PLURAL,
    UPDATED_AT_VERBOSE_NAME,
    USER_VERBOSE_NAME,
)

User = get_user_model()


class BaseModel(models.Model):
    """Абстрактная модель с общими полями."""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name=NAME_VERBOSE_NAME
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_LENGTH, unique=True, verbose_name=SLUG_VERBOSE_NAME
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=CREATED_AT_VERBOSE_NAME
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=UPDATED_AT_VERBOSE_NAME
    )

    class Meta:
        """Метакласс для абстрактной модели с общими полями."""

        abstract = True
        ordering = (NAME_ORDERING,)


class Category(BaseModel):
    """Модель категории товаров."""

    image = models.ImageField(
        upload_to=CATEGORY_IMAGE_PATH, verbose_name=IMAGE_VERBOSE_NAME
    )

    class Meta:
        """Метакласс для модели категории товаров."""

        verbose_name = CATEGORY_VERBOSE_NAME
        verbose_name_plural = CATEGORY_VERBOSE_NAME_PLURAL

    def __str__(self):
        """Возвращает строковое представление категории."""
        return self.name


class SubCategory(BaseModel):
    """Модель подкатегории товаров."""

    image = models.ImageField(
        upload_to=SUBCATEGORY_IMAGE_PATH, verbose_name=IMAGE_VERBOSE_NAME
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name=CATEGORY_VERBOSE_NAME_FIELD,
    )

    class Meta:
        """Метакласс для модели подкатегории товаров."""

        verbose_name = SUBCATEGORY_VERBOSE_NAME
        verbose_name_plural = SUBCATEGORY_VERBOSE_NAME_PLURAL

    def __str__(self):
        """Возвращает строковое представление подкатегории."""
        return f'{self.category.name} -> {self.name}'


class Product(BaseModel):
    """Модель товара."""

    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=SUBCATEGORY_VERBOSE_NAME_FIELD,
    )
    price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        verbose_name=PRICE_VERBOSE_NAME,
    )
    image_small = models.ImageField(
        upload_to=PRODUCT_SMALL_IMAGE_PATH,
        verbose_name=SMALL_IMAGE_VERBOSE_NAME,
    )
    image_medium = models.ImageField(
        upload_to=PRODUCT_MEDIUM_IMAGE_PATH,
        verbose_name=MEDIUM_IMAGE_VERBOSE_NAME,
    )
    image_large = models.ImageField(
        upload_to=PRODUCT_LARGE_IMAGE_PATH,
        verbose_name=LARGE_IMAGE_VERBOSE_NAME,
    )

    class Meta:
        """Метакласс для модели товара."""

        verbose_name = PRODUCT_VERBOSE_NAME
        verbose_name_plural = PRODUCT_VERBOSE_NAME_PLURAL

    def __str__(self):
        """Возвращает строковое представление товара."""
        return self.name


class CartItem(models.Model):
    """Модель элемента корзины."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name=USER_VERBOSE_NAME,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name=PRODUCT_VERBOSE_NAME,
    )
    quantity = models.PositiveIntegerField(
        default=1, verbose_name=QUANTITY_VERBOSE_NAME
    )
    added_at = models.DateTimeField(
        auto_now_add=True, verbose_name=ADDED_AT_VERBOSE_NAME
    )

    class Meta:
        """Метакласс для модели элемента корзины."""

        verbose_name = CART_ITEM_VERBOSE_NAME
        verbose_name_plural = CART_ITEM_VERBOSE_NAME_PLURAL
        unique_together = ['user', 'product']

    def __str__(self):
        """Возвращает строковое представление элемента корзины."""
        return f'{self.user.username}: {self.product.name} x {self.quantity}'

    @property
    def total_price(self) -> Decimal:
        """Возвращает общую стоимость позиции в корзине."""
        return self.product.price * self.quantity
