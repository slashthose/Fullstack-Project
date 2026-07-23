from .cart import Cart
from .models import Wishlist

def cart_count(request):
    return {'cart_count': len(Cart(request))}
def wishlist_count(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter( user=request.user).count()
    else:
        count = 0
    return { "wishlist_count":count}