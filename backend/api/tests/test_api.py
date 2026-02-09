"""
Тесты для API приложения магазина.

Этот модуль содержит юнит-тесты для проверки функциональности API:
- GET запросы для получения данных
- POST запросы для создания/обновления данных
"""

import os
import tempfile
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from shop.models import CartItem, Category, Product, SubCategory

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class CartAPITestCase(TestCase):
    """Тесты для API корзины."""

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
        import uuid

        from django.core.files.base import ContentFile

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

    def test_get_cart_items_authenticated(self):
        """Тест GET запроса для получения содержимого корзины
        авторизованного пользователя.
        """
        # Создаем элементы корзины для пользователя
        cart_item = CartItem.objects.create(
            user=self.user, product=self.product, quantity=2
        )

        # Выполняем GET запрос к эндпоинту корзины
        url = reverse(
            'cart-list'
        )  # Это маршрут для получения списка элементов корзины
        response = self.client.get(url)

        # Проверяем успешность запроса
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что в ответе есть хотя бы один элемент
        if 'results' in response.data:
            self.assertGreater(len(response.data['results']), 0)

            # Проверяем, что возвращенные данные содержат ожидаемый продукт
            returned_item = response.data['results'][0]
            self.assertEqual(returned_item['product']['id'], self.product.id)
            self.assertEqual(returned_item['quantity'], cart_item.quantity)
        else:
            # Если пагинация не используется, данные могут быть в response.data
            self.assertGreater(len(response.data), 0)
            returned_item = response.data[0]
            self.assertEqual(returned_item['product']['id'], self.product.id)
            self.assertEqual(returned_item['quantity'], cart_item.quantity)

    def test_post_cart_item_authenticated(self):
        """Тест POST запроса для добавления товара в корзину
        авторизованного пользователя.
        """
        # Подготовим данные для отправки
        url = reverse(
            'cart-list'
        )  # Это маршрут для добавления элемента в корзину
        data = {'product': self.product.id, 'quantity': 3}

        # Выполняем POST запрос
        response = self.client.post(url, data, format='json')

        # Проверяем успешность запроса
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что элемент действительно добавлен в корзину
        self.assertEqual(CartItem.objects.count(), 1)
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.user, self.user)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 3)

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
