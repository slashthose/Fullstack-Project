from core.models import Product
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def _key(self, product_id, size):
        return f"{product_id}_{size or 'default'}"

    def add(self, product, quantity=1, size=None):
        key = self._key(product.id, size)
        if key in self.cart:
            self.cart[key]['quantity'] += quantity
        else:
            self.cart[key] = {
                'product_id': product.id,
                'quantity': quantity,
                'size': size,
            }
        self.save()

    def update(self, product_id, size, quantity):
        key = self._key(product_id, size)
        if key in self.cart:
            if quantity <= 0:
                del self.cart[key]
            else:
                self.cart[key]['quantity'] = quantity
            self.save()

    def remove(self, product_id, size):
        key = self._key(product_id, size)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True

    def __iter__(self):
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        products_by_id = {p.id: p for p in products}
        for item in self.cart.values():
            product = products_by_id.get(item['product_id'])
            if not product:
                continue
            yield {
                'product': product,
                'quantity': item['quantity'],
                'size': item['size'],
                'subtotal': product.price * item['quantity'],
            }

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())