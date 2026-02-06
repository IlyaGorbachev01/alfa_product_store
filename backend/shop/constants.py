"""Константы для приложения магазина."""

# Константы для полей моделей
MAX_NAME_LENGTH = 255
MAX_SLUG_LENGTH = 255
PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2

# Пути для загрузки изображений
CATEGORY_IMAGE_PATH = 'categories/'
SUBCATEGORY_IMAGE_PATH = 'subcategories/'
PRODUCT_SMALL_IMAGE_PATH = 'products/small/'
PRODUCT_MEDIUM_IMAGE_PATH = 'products/medium/'
PRODUCT_LARGE_IMAGE_PATH = 'products/large/'

# Человекочитаемые имена моделей
CATEGORY_VERBOSE_NAME = 'Категория'
CATEGORY_VERBOSE_NAME_PLURAL = 'Категории'
SUBCATEGORY_VERBOSE_NAME = 'Подкатегория'
SUBCATEGORY_VERBOSE_NAME_PLURAL = 'Подкатегории'
PRODUCT_VERBOSE_NAME = 'Продукт'
PRODUCT_VERBOSE_NAME_PLURAL = 'Продукты'
CART_ITEM_VERBOSE_NAME = 'Элемент корзины'
CART_ITEM_VERBOSE_NAME_PLURAL = 'Элементы корзины'

# Человекочитаемые имена полей
NAME_VERBOSE_NAME = 'Наименование'
SLUG_VERBOSE_NAME = 'Slug'
IMAGE_VERBOSE_NAME = 'Изображение'
CATEGORY_VERBOSE_NAME_FIELD = 'Категория'
SUBCATEGORY_VERBOSE_NAME_FIELD = 'Подкатегория'
PRICE_VERBOSE_NAME = 'Цена'
SMALL_IMAGE_VERBOSE_NAME = 'Изображение (маленькое)'
MEDIUM_IMAGE_VERBOSE_NAME = 'Изображение (среднее)'
LARGE_IMAGE_VERBOSE_NAME = 'Изображение (большое)'
QUANTITY_VERBOSE_NAME = 'Количество'
USER_VERBOSE_NAME = 'Пользователь'
ADDED_AT_VERBOSE_NAME = 'Дата добавления'
CREATED_AT_VERBOSE_NAME = 'Дата создания'
UPDATED_AT_VERBOSE_NAME = 'Дата обновления'

# Поля для сортировки
NAME_ORDERING = 'name'
