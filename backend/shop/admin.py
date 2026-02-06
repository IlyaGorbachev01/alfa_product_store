"""Модуль административной панели для приложения магазина."""

from django.contrib import admin

from .models import CartItem, Category, Product, SubCategory


class BaseInline(admin.TabularInline):
    """Базовый inline-класс для моделей с полями name и slug."""

    extra = 1
    prepopulated_fields = {'slug': ('name',)}


class SubCategoryInline(BaseInline):
    """Inline-класс для отображения подкатегорий внутри категории."""

    model = SubCategory


class ProductInline(BaseInline):
    """Inline-класс для отображения продуктов внутри подкатегории."""

    model = Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Административный класс для модели Category."""

    list_display = ('name', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}  # Автогенерация slug из name
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    inlines = [SubCategoryInline]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """Административный класс для модели SubCategory."""

    list_display = ('name', 'category', 'slug', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('name', 'slug', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('category', 'name')
    raw_id_fields = ('category',)  # Для удобства выбора категории
    inlines = [ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Административный класс для модели Product."""

    list_display = ('name', 'subcategory', 'price', 'slug', 'created_at')
    list_filter = ('subcategory__category', 'subcategory', 'created_at')
    search_fields = (
        'name',
        'slug',
        'subcategory__name',
        'subcategory__category__name',
    )
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    raw_id_fields = ('subcategory',)

    # Группировка полей в fieldsets
    fieldsets = (
        (
            'Основная информация',
            {'fields': ('name', 'slug', 'subcategory', 'price')},
        ),
        (
            'Изображения',
            {
                'fields': ('image_small', 'image_medium', 'image_large'),
                'classes': ('collapse',),  # Сворачиваемая секция
            },
        ),
        (
            'Даты',
            {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)},
        ),
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Административный класс для модели CartItem."""

    list_display = ('user', 'product', 'quantity', 'total_price', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('added_at', 'total_price')
    raw_id_fields = ('user', 'product')
