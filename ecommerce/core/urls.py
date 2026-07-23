from django.urls import path
from . import views

urlpatterns =[
    path('',views.index,name='index'),

    path('category/<str:category_name>/', views.category_view, name='category_view'),

    path('cart/', views.cart_view, name='cart_view'),

    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('cart/update/<int:product_id>/', views.update_cart_item, name='update_cart_item'),

    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path("wishlist/", views.wishlist_view,name="wishlist",),
    path("wishlist/add/<int:product_id>/",views.add_to_wishlist,name="add_to_wishlist"),
    path("wishlist/remove/<int:product_id>/",views.remove_from_wishlist,name="remove_from_wishlist"),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search_view, name='search_view'),
    path('checkout/', views.checkout_view, name='checkout_view'),
    path('place-order/', views.place_order, name='place_order'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_confirmation, name='order_detail'),



]
