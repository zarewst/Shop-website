from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.

# Модель Категории
class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название категории')
    image = models.ImageField(upload_to='categories/', verbose_name='Изображения', blank=True, null=True)
    slug = models.SlugField(unique=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               verbose_name='Категория', related_name='subcategories',
                               null=True, blank=True)

    def get_absolute_url(self):  # Умная ссылка категорий
        return reverse('category_detail', kwargs={'slug': self.slug})

    def get_image(self):
        if self.image:  # Если есть фото
            return self.image.url  # тогда верни фото категории
        else:  # В противном случае верни что то по умолчанию
            return 'https://bprix.ru/image/cache/catalog/Plintys/Russia/no_foto-700x700.jpg'

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'Категория: pk={self.pk}, title={self.title}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


# Модель Продукта
class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название продукта')
    price = models.FloatField(verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    description = models.TextField(default='Здесь скоро будет описание', verbose_name='Описание товара')
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name='Категория', related_name='products')
    slug = models.SlugField(unique=True, null=True)
    size = models.IntegerField(default=30, verbose_name='Размер в мм')
    color = models.CharField(max_length=50, default='Серебро', verbose_name='цвет/материал')

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    # Метод для получение 1 картинки из списка картинок продукта
    def get_first_photo(self):
        if self.images:
            try:
                return self.images.first().image.url
            except:
                return 'https://bprix.ru/image/cache/catalog/Plintys/Russia/no_foto-700x700.jpg'
        else:
            return 'https://bprix.ru/image/cache/catalog/Plintys/Russia/no_foto-700x700.jpg'

    def __str__(self):
        return self.title

    def __repr__(self):
        return f'Товар: pk={self.pk}, title={self.title}, price={self.price}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


# Модель Галереи товаров
class Gallery(models.Model):
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


# Моделька Отзывов
class Review(models.Model):
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата коментария')

    def __str__(self):
        return self.author.username

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class FavouriteProducts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Избранный Товар'
        verbose_name_plural = 'Избранные Товары'

# ----------------------------------------------------------------------------------------------------

# Модель покупателя
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=300, default='', verbose_name='Имя пользователя')
    last_name = models.CharField(max_length=300, default='', verbose_name='Фамилия пользователя')

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'



class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping = models.BooleanField(default=True)


    def __str__(self):
        return str(self.pk) + ''

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # Здесь будут методы которые будут считать общ стоимость Заказа и кол-во продуктов
    @property
    def get_cart_total_price(self):
        order_products = self.orderproduct_set.all()
        total_price = sum([product.get_total_price for product in order_products])  # [500, 400]
        return total_price

    @property
    def get_cart_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([product.quantity for product in order_products])  # [1, 2]
        return total_quantity


# Заказаный продукт (Корзина)
class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    addet_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заказаный продукт'
        verbose_name_plural = 'Заказаные продукты'

    # Метод который будит считать стоисмость продуктов в кол-ве
    @property
    def get_total_price(self):
        total_price = self.product.price * self.quantity
        return total_price



# Модель Адреса доставки
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=300)
    region = models.CharField(max_length=300)
    phone = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Адресс доставки'
        verbose_name_plural = 'Адреса доставок'


# Сделать модель города и что бы пользователь мог выбрать конкретный город которые есть в наличии




















