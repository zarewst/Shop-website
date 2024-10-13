from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe

# Register your models here.

class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'get_count')  # то что хочу видеть
    prepopulated_fields = {'slug': ('title',)}

    # Метод для получения количество товаров в каждой категории
    def get_count(self, obj):
        if obj.products:
            return str(len(obj.products.all()))
        else:
            return '0'

    get_count.short_description = 'Количество'





@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'quantity', 'price', 'size', 'color', 'created_at', 'get_photo')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('price', 'quantity', 'size', 'color', 'category')  # Указал какие поля можно редактировать
    list_display_links = ('title',)
    list_filter = ('title', 'price', 'category')  # Указали по каким полям отфильтровать
    inlines = [GalleryInline]

    # Метод для получения фото продукта и отправки в Админку
    def get_photo(self, obj):
        if obj.images:   # Если у объекта есть картинки
            try:  # попытайся
                return mark_safe(f'<img src="{obj.images.all()[0].image.url}" width="75">')  # Вернуть картинку
            except:
                return 'шиш'
        else:
            return 'кыш'

    get_photo.short_description = 'Картинка'


admin.site.register(Review)