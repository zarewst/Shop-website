from django import template
from store.models import Category, FavouriteProducts


register = template.Library()

# Функция для получения глав категорий
@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent=None)



# Функция для получения подкатегорий по категории
@register.simple_tag()
def get_subcategories(category):
    return Category.objects.filter(parent=category)



# Функция для сортировки по цвету, размеру, цене
@register.simple_tag()
def get_sorted():
    sorters = [
        {
            'title': 'По цене',
            'sorters': [
                ('price', 'От самых дешёвых'),
                ('-price', 'От самых дорогих'),
            ]
        },

        {
            'title': 'По цвету',
            'sorters': [
                ('color', 'От А до Я'),
                ('-color', 'От Я до А'),
            ]
        },

        {
            'title': 'По размеру',
            'sorters': [
                ('size', 'От самых мальньких'),
                ('-size', 'От самых больших'),
            ]
        }
    ]
    return sorters


@register.simple_tag()
def get_favourite_products(user):
    fav = FavouriteProducts.objects.filter(user=user)
    products = [i.product for i in fav]  # Делаем генератором что бы получить список продуктов без user
    return products













