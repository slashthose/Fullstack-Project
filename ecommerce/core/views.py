from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.models import Product,Category
from core.forms import *
from .cart import Cart
from core.models import Order, OrderItem
import razorpay
import json

# Create your views here.
def add_product(request):
    return render(request,'core/add_product.html')
def index(request):
    products = Product.objects.all().order_by('-id')[:12]
    return render(request, 'core/index.html', {'products': products})
def category_view(request, category_name):
    category = get_object_or_404(Category, category_name__iexact=category_name)
    products = Product.objects.filter(category=category)  # this actually still works the same for M2M
    return render(request, 'core/category.html', {
        'products': products,
        'category': category,
    })

def cart_view(request):
    cart = Cart(request)
    cart_items = list(cart)
    cart_subtotal = sum(item['subtotal'] for item in cart_items)
    return render(request, 'core/cart.html', {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
    })

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    size = request.POST.get('size') or None
    Cart(request).add(product=product, quantity=quantity, size=size)
    return JsonResponse({'cart_count': len(Cart(request))})

@require_POST
def update_cart_item(request, product_id):
    size = request.POST.get('size') or None
    quantity = int(request.POST.get('quantity', 1))
    Cart(request).update(product_id, size, quantity)
    return redirect('cart_view')


@require_POST
def remove_from_cart(request, product_id):
    size = request.POST.get('size') or None
    Cart(request).remove(product_id, size)
    return redirect('cart_view')


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product")
    context = {"wishlist_items": wishlist_items}
    return render( request,"core/wishlist.html",context)

@login_required
def add_to_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    Wishlist.objects.get_or_create(

        user=request.user,

        product=product

    )

    wishlist_count = Wishlist.objects.filter(

        user=request.user

    ).count()

    return JsonResponse({

        "success":True,

        "wishlist_count":wishlist_count

    })

@login_required
def remove_from_wishlist(request,product_id):

    Wishlist.objects.filter(

        user=request.user,

        product_id=product_id

    ).delete()

    wishlist_count = Wishlist.objects.filter(

        user=request.user

    ).count()

    return JsonResponse({

        "success":True,

        "wishlist_count":wishlist_count

    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Related products: same category, excluding this product itself
    related_products = Product.objects.filter(
        category__in=product.category.all()
    ).exclude(id=product.id).distinct()[:4]

    return render(request, 'core/product detail.html', {
        'product': product,
        'related_products': related_products,
    })

def search_view(request):
    query = request.GET.get('q', '').strip()
    products = []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(desc__icontains=query)
        ).distinct()
    return render(request, 'core/search_results.html', {
        'products': products,
        'query': query,
    })


@login_required
def checkout_view(request):
    cart = Cart(request)
    cart_items = list(cart)
    total = sum(item['subtotal'] for item in cart_items)

    return render(request, "core/checkout.html", {
        "cart_items": cart_items,
        "total": total,
    })


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def place_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    cart = Cart(request)
    cart_items = list(cart)

    if not cart_items:
        return JsonResponse({"error": "Cart is empty"}, status=400)

    total = sum(item["subtotal"] for item in cart_items)

    order = Order.objects.create(
        user=request.user,
        status="pending",
        total_amount=total,
        full_name=request.POST["full_name"],
        phone=request.POST["phone"],
        address_line=request.POST["address_line"],
        city=request.POST["city"],
        pincode=request.POST["pincode"],
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            name=item["product"].name,
            price=item["product"].price,
            quantity=item["quantity"],
        )

    razorpay_order = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": 1,
    })

    order.razorpay_order_id = razorpay_order["id"]
    order.save()

    return JsonResponse({
        "razorpay_order_id": razorpay_order["id"],
        "amount": int(total * 100),
        "key_id": settings.RAZORPAY_KEY_ID,
        "internal_order_id": order.id,
    })

@login_required
def verify_payment(request):
    if request.method != "POST":
        return JsonResponse({"status": "failed"}, status=405)

    data = json.loads(request.body)

    params = {
        "razorpay_order_id": data["razorpay_order_id"],
        "razorpay_payment_id": data["razorpay_payment_id"],
        "razorpay_signature": data["razorpay_signature"],
    }

    try:
        client.utility.verify_payment_signature(params)
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"status": "failed"}, status=400)

    order = get_object_or_404(Order, id=data["internal_order_id"])

    order.status = "paid"
    order.razorpay_payment_id = data["razorpay_payment_id"]
    order.save()

    for item in order.items.all():
        product = item.product
        product.product_available_count -= item.quantity
        product.save()

    Cart(request).clear()

    return JsonResponse({"status": "success"})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'core/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/order_history.html', {'orders': orders})