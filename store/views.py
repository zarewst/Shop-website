from random import randint

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from .models import *
from .forms import ReviewForm, LoginForm, RegistrationForm, CustomerForm, ShippingForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .utils import CartForAuthenticatedUser, get_cart_info
from django.contrib.auth.mixins import LoginRequiredMixin
from shop import settings
import stripe


# Create your views here.

class ProductList(ListView):
    model = Product
    context_object_name = 'categories'
    extra_context = {
        'title': 'Магазин TOTEMBO'
    }
    template_name = 'store/product_list.html'

    #  Функция для получения подкатегорий из категории
    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories


# Вьюшка для страницы категорий
class CategoryView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category_page.html'

    def get_queryset(self):
        sort_field = self.request.GET.get('sort')
        type_field = self.request.GET.get('type')
        if type_field:
            products = Product.objects.filter(category__slug=type_field)
            return products
        main_category = Category.objects.get(slug=self.kwargs['slug'])  # Получили глав категорию
        subcategories = main_category.subcategories.all()  # Получили подкатегории
        products = Product.objects.filter(category__in=subcategories)  # Получаем продукты всех подкатегорий

        if sort_field:
            products = products.order_by(sort_field)

        return products

    # Метод Динамического возврата ДАнных
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        main_category = Category.objects.get(slug=self.kwargs['slug'])
        context['category'] = main_category
        context['title'] = f'Категория: {main_category.title}'
        return context


# Вьющка для страницы детали товара
class ProductDetail(DetailView):  # Данный класс автоматом будит искать страницу product_detail.html
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'{product.category}: {product.title}'

        products = Product.objects.all()
        data = []  # Сюда рандомно будут добавляться продукты максимум 4
        for i in range(4):
            random_index = randint(0, len(products) - 1)  # Получаем рандомное число
            p = products[random_index]
            if p not in data:
                data.append(p)
        context['products'] = data

        context['reviews'] = Review.objects.filter(product=product)

        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()

        return context


# Функция для сохранения комментариев
def save_review(request, product_slug):
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        product = Product.objects.get(slug=product_slug)
        review.product = product
        review.save()
    else:
        pass
    return redirect('product_detail', product_slug)


# Функция для страницы Логина и регистрации
def login_registration(request):
    context = {
        'title': 'Войти или зарегистрироваться',
        'login_form': LoginForm(),
        'register_form': RegistrationForm()
    }

    return render(request, 'store/login_registration.html', context)


def user_login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, 'Вы вошли в Аккаунт')
        return redirect('product_list')
    else:
        messages.warning(request, 'Не верный логин или пароль')
        return redirect('login_registration')


def user_logout(request):
    logout(request)
    messages.warning(request, 'Вы вышли из Аккаунта')
    return redirect('product_list')


def register(request):
    form = RegistrationForm(data=request.POST)
    if form.is_valid():
        user = form.save()
        messages.success(request, 'Регистрация прошла успешно. Войдите в Аккаунт')
    else:
        for field in form.errors:
            messages.warning(request, form.errors[field].as_text())

    return redirect('login_registration')


def save_favourite_product(request, product_slug):
    user = request.user if request.user.is_authenticated else None
    product = Product.objects.get(slug=product_slug)
    favourite_products = FavouriteProducts.objects.filter(user=user)
    print(f'Список продуктов {product}')
    print(f'Список изб  продуктов {FavouriteProducts}')
    if user:
        if product in [i.product for i in favourite_products]:
            fav_product = FavouriteProducts.objects.get(user=user, product=product)
            fav_product.delete()
        else:
            FavouriteProducts.objects.create(user=user, product=product)

    next_page = request.META.get('HTTP_REFERER', 'product_list')

    return redirect(next_page)


# Класс для страницы избранного
class FavouriteProductView(LoginRequiredMixin, ListView):
    model = FavouriteProducts
    context_object_name = 'products'
    template_name = 'store/favourite_products.html'
    login_url = 'login_registration'

    def get_queryset(self):
        user = self.request.user
        favs = FavouriteProducts.objects.filter(user=user)
        products = [i.product for i in favs]
        return products


# Функция для страницы корзины

def cart(request):
    if request.user.is_authenticated:
        cart_info = get_cart_info(request)
        context = {
            'cart_total_quantity': cart_info['cart_total_quantity'],
            'order': cart_info['order'],
            'products': cart_info['products']
        }
        return render(request, 'store/cart.html', context)
    else:
        messages.warning(request, 'Авторизуйтесь для перехода в корзину')
        return redirect('login_registration')


def to_cart(request, product_id, action):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request, product_id, action)
        return redirect('cart')
    else:
        messages.error(request, 'Авторизуйтесь, что бы сделать покупки')
        return redirect('login_registration')


# Функция которая отвечает за страницу оформления заказа
def checkout(request):
    cart_info = get_cart_info(request)

    context = {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'order': cart_info['order'],
        'items': cart_info['products'],
        'title': 'Оформление заказа',

        'customer_form': CustomerForm(),
        'shipping_form': ShippingForm()

    }

    return render(request, 'store/checkout.html', context)


# Функция для оформления заказа нужна библиотека stripe

def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()

        total_price = cart_info['cart_total_price']
        total_quantity = cart_info['cart_total_quantity']
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Товары с TOTEMBO'
                    },
                    'unit_amount': int(total_price * 100)
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout'))
        )
        return redirect(session.url, 303)


def successPayment(request):
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()
    messages.success(request, 'Оплата прошла успешно. Наш менеджер с вами свяжется')
    return redirect('product_list')


# Функция для очистки корзины при нажатии на кнопку
def clear_cart(request):
    user_cart = CartForAuthenticatedUser(request)
    order = user_cart.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for order_product  in order_products:
        quantity = order_product.quantity
        product = order_product.product
        print(f'Продукты которые получаем: {quantity, product}')
        order_product.delete()
        product.quantity += quantity
        product.save()
    return redirect('cart')








