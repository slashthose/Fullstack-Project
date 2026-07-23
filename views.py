# shop/views.py
from django.shortcuts import render
from .models import Product

def landing_page(request):
    # Fetch 4 featured products for the preview section
    featured_products = Product.objects.all()[:4]

    context = {
        'featured_products': featured_products
    }
    return render(request, 'shop/landing.html', context)