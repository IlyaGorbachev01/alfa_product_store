"""
Дополнительные тесты для API приложения магазина.

Этот модуль содержит дополнительные тесты для проверки функциональности API:
- GET запросы для получения данных
- POST запросы для создания/обновления данных
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
from rest_framework.test import APIClient

from shop.models import Category, Product, SubCategory

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PublicAPITestCase(TestCase):
    """Тесты для публичных API (без аутентификации)."""

    def setUp(self):
        """Подготовка тестовых данных."""
        self.client = APIClient()

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

    def test_category_list_endpoint(self):
        """Тест GET запроса для получения списка категорий."""
        url = reverse('category-list')
        response = self.client.get(url)
        # Ожидаем успешный ответ, так как этот эндпоинт публичный
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_list_endpoint(self):
        """Тест GET запроса для получения списка продуктов."""
        url = reverse('product-list')
        response = self.client.get(url)
        # Ожидаем успешный ответ, так как этот эндпоинт публичный
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
