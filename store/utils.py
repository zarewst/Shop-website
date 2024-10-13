from .models import Product, Order, OrderProduct, Customer


class CartForAuthenticatedUser:
    def __init__(self, request, product_id=None, action=None):
        self.user = request.user

        if product_id and action:
            self.add_or_delete(product_id, action)

    # Метод который будит возвращать информацию о корзине
    def get_cart_info(self):
        customer, created = Customer.objects.get_or_create(user=self.user)  # Создаём или получаем покупателя

        order, created = Order.objects.get_or_create(customer=customer)  # Создаём или получаем заказ
        order_products = order.orderproduct_set.all()  # Получаем все заказанные продукты заказа

        cart_total_quantity = order.get_cart_total_quantity
        cart_total_price = order.get_cart_total_price

        return {
            'cart_total_quantity': cart_total_quantity,
            'cart_total_price': cart_total_price,
            'order': order,
            'products': order_products
        }

    # Метод который будит добавлять и удалять из корзины
    def add_or_delete(self, product_id, action):
        order = self.get_cart_info()['order']
        product = Product.objects.get(pk=product_id)
        order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)

        if action == 'add' and product.quantity > 0:
            order_product.quantity += 1  # +1 В заказанные продукты
            product.quantity -= 1  # На складе -1
        else:
            order_product.quantity -= 1  # -1 В заказанные продукты
            product.quantity += 1  # На складе +1

        product.save()
        order_product.save()

        if order_product.quantity <= 0:
            order_product.delete()

    # Метод для очистки корзины после успешной оплаты
    def clear(self):
        order = self.get_cart_info()['order']
        order_products = order.orderproduct_set.all()
        for product in order_products:
            product.delete()
        order.save()


# Функция которая будит возвращать информацию о корзине из Класса
def get_cart_info(request):
    cart = CartForAuthenticatedUser(request)
    cart_info = cart.get_cart_info()

    return {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'cart_total_price': cart_info['cart_total_price'],
        'order': cart_info['order'],
        'products': cart_info['products']
    }
