from django.urls import path
from . import views

urlpatterns = [
    path('products', views.products, name = 'products'),
    path('product', views.detailed_product, name = 'detailed_product'),
    path('add_to_cart', views.add_to_cart, name = 'add_to_cart'),
    path('remove_from_cart', views.remove_from_cart, name = 'remove_from_cart'),
    path('change_cart_quantity', views.change_cart_quantity, name = 'change_cart_quantity'),
    path('cart', views.cart, name = 'cart'),
    path('history', views.history, name = 'history'),
    path('payment', views.payment, name = 'payment'),
    path('webhook', views.webhook, name = 'webhook'),
]