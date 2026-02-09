"""
Дополнительные тесты для API корзины.

Этот модуль содержит тесты для проверки функциональности корзины:
- POST запросы для различных действий с корзиной
"""

import os
import tempfile
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from shop.models import CartItem, Category, Product, SubCategory

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class CartPostAPITestCase(TestCase):
    """Дополнительные тесты POST запросов для API корзины."""

    def setUp(self):
        """Подготовка тестовых данных."""
        self.client = APIClient()

        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
        )

        # Создаем токен для аутентификации
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Создаем тестовые изображения в нужной директории
        # Создаем изображения с помощью ContentFile
        image = Image.new('RGB', (100, 100))
        tmp_img = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image.save(tmp_img, 'JPEG')
        tmp_img.close()

        # Создаем тестовые данные для магазина
        self.category = Category(
            name='Тестовая категория', slug='test-category'
        )
        # Сохраняем изображение в поле
        with open(tmp_img.name, 'rb') as img_file:
            self.category.image.save(
                f'test_category_{uuid.uuid4()}.jpg',
                ContentFile(img_file.read()),
                save=False,
            )
        self.category.save()

        # Создаем подкатегорию
        self.subcategory = SubCategory(
            name='Тестовая подкатегория',
            slug='test-subcategory',
            category=self.category,
        )
        with open(tmp_img.name, 'rb') as img_file:
            self.subcategory.image.save(
                f'test_subcategory_{uuid.uuid4()}.jpg',
                ContentFile(img_file.read()),
                save=False,
            )
        self.subcategory.save()

        # Создаем продукт
        self.product = Product(
            name='Тестовый продукт',
            slug='test-product',
            subcategory=self.subcategory,
            price=Decimal('999.99'),
        )
        # Сохраняем разные изображения для каждого размера
        with open(tmp_img.name, 'rb') as img_file:
            self.product.image_small.save(
                f'test_small_{uuid.uuid4()}.jpg',
                ContentFile(img_file.read()),
                save=False,
            )
        with open(tmp_img.name, 'rb') as img_file:
            self.product.image_medium.save(
                f'test_medium_{uuid.uuid4()}.jpg',
                ContentFile(img_file.read()),
                save=False,
            )
        with open(tmp_img.name, 'rb') as img_file:
            self.product.image_large.save(
                f'test_large_{uuid.uuid4()}.jpg',
                ContentFile(img_file.read()),
                save=False,
            )
        self.product.save()

        # Удаляем временный файл
        os.unlink(tmp_img.name)

    def test_post_summary_cart_authenticated(self):
        """Тест GET запроса для получения сводки корзины
        авторизованного пользователя.
        """
        # Сначала добавим элемент в корзину
        CartItem.objects.create(
            user=self.user, product=self.product, quantity=2
        )

        # Выполняем GET запрос к эндпоинту сводки корзины
        url = reverse(
            'cart-summary'
        )  # Это маршрут для получения сводки корзины
        response = self.client.get(url)

        # Проверяем успешность запроса
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем наличие ожидаемых полей в ответе
        self.assertIn('items', response.data)
        self.assertIn('total_items', response.data)
        self.assertIn('total_price', response.data)

    def test_post_update_cart_item_quantity(self):
        """Тест PUT запроса для изменения количества товара в корзине."""
        # Сначала добавим элемент в корзину
        cart_item = CartItem.objects.create(
            user=self.user, product=self.product, quantity=2
        )

        # Подготовим данные для обновления
        url = reverse(
            'cart-detail', kwargs={'pk': cart_item.pk}
        )  # Это маршрут для обновления элемента корзины
        data = {'product': self.product.id, 'quantity': 5}

        # Выполняем PUT запрос
        response = self.client.put(url, data, format='json')

        # Проверяем успешность запроса
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что количество обновилось
        updated_cart_item = CartItem.objects.get(pk=cart_item.pk)
        self.assertEqual(updated_cart_item.quantity, 5)

    def tearDown(self):
        """Очистка после тестов."""
        # Удаляем временные файлы изображений
        # Удаляем файлы, связанные с продуктом
        for image_field in [
            self.category.image,
            self.subcategory.image,
            self.product.image_small,
            self.product.image_medium,
            self.product.image_large,
        ]:
            if image_field and os.path.exists(image_field.path):
                os.remove(image_field.path)
