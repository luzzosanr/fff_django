from django.shortcuts import get_object_or_404
from store.models import Product, Item, Command
from accounts.models import BrandUserProfile
from rest_framework.response import Response
from rest_framework.decorators import api_view
import stripe
import os

stripe.api_key = os.environ.get('STRIPE_API_KEY_TEST')

@api_view(['GET'])
def products(request):
    """
    :param request: product.name, product.slug, product.price, product.image.url, product.brand_name
    :return: Products filtered
    """
    return Response({"products": [{"name": product.name, "slug": product.slug, "price": product.price, "image": product.image.url, "brand": product.brand_name} for product in Product.objects.filter(is_available = True)]})

@api_view(['GET'])
def detailed_product(request):
    """
    :param request: brand, slug
    :return: Detailed product info
    """
    
    brand = get_object_or_404(BrandUserProfile, name = request.GET.get('brand'))
    product = get_object_or_404(Product, slug = request.GET.get('slug'), brand = brand, is_available = True)
    return Response({"product": {"name": product.name, "price": product.price, "image": product.image.url, "description": product.description, "stock": product.stock}})

@api_view(['POST'])
def add_to_cart(request):
    """
    :summary: Adds product to the user's cart
    :param request: brand, slug, user
    """
    
    if not request.user.is_authenticated or request.user.role != 'SHOPPER':
        return Response({'status': 'not logged'})
    
    brand = get_object_or_404(BrandUserProfile, name = request.data.get('brand'))
    product = get_object_or_404(Product, slug = request.data.get('slug'), brand = brand, is_available = True)
    product.add_to_cart(request.user.profile)
    return Response({"status": "success"})

@api_view(['POST'])
def remove_from_cart(request):
    if not request.user.is_authenticated or request.user.role != 'SHOPPER':
        return Response({'status': 'not logged'})
    
    brand = get_object_or_404(BrandUserProfile, name = request.data.get('brand'))
    product = get_object_or_404(Product, slug = request.data.get('slug'), brand = brand, is_available = True)
    product.remove_from_cart(request.user.profile)
    return Response({"message": "success"})

@api_view(['POST'])
def change_cart_quantity(request):
    if not request.user.is_authenticated or request.user.role != 'SHOPPER':
        return Response({'status': 'not logged'})
    
    brand = get_object_or_404(BrandUserProfile, name = request.data.get('brand'))
    product = get_object_or_404(Product, slug = request.data.get('slug'), brand = brand, is_available = True)
    product.change_quantity(request.user.profile, request.data.get('quantity'))
    return Response({"status": "success"})

@api_view(['GET'])
def cart(request):
    if not request.user.is_authenticated or request.user.role != 'SHOPPER':
        return Response({'status': 'not logged'})
    
    cart_items = Item.objects.filter(buyer = request.user.profile, bought = False)
    return Response({"status": "success", "cart_items": [
        {
            "name": item.product.name,
            "price": item.product.price,
            "image": item.product.image.url,
            "quantity": item.quantity,
            "total": item.total_price,
            "slug": item.product.slug,
            "brand": item.product.brand_name
        } for item in cart_items]})


@api_view(['GET'])
def history(request):
    """
    :param request: user
    :return: list of bought items buy the given user
    """
    if not request.user.is_authenticated or request.user.role != 'SHOPPER':
        return Response({'status': 'not logged'})
    
    return Response({'status': 'success', 'history': [{'name': item.product.name, 'image': item.product.image.url, 'brand': item.product.brand_name, "date": item.data_time, "slug": item.product.slug, "price": item.price_on_buying, "quantity": item.quantity} for item in Item.objects.filter(buyer = request.user.profile, bought = True)]})


@api_view(['POST'])
def payment(request):
    if not request.user.is_authenticated or request.user.role != 'SHOPPER':
        return Response({'status': 'not logged'})
    
    if Item.is_cart_empty(request.user.profile):
        return Response({'status': 'empty_cart'})
    
    items = Item.objects.filter(buyer = request.user.profile, bought = False)
    for item in items:
        if item.product.stock != None and item.product.stock < item.quantity:
            item.quantity = item.product.stock
            item.product.save()
            return Response({'status': 'not_enough_stock', 'product': {'slug': item.product.slug, 'brand': item.product.brand_name, 'name': item.product.name, 'stock': item.product.stock}})
    
    checkout_session = stripe.checkout.Session.create(
        line_items = [
            {
                "quantity": item.quantity,
                "description": item.product.description,
                "amount": item.product.price,
                "currency": 'eur',
                "name": item.product.name
            }
            for item in Item.objects.filter(buyer = request.user.profile, bought = False)
        ],
        mode = 'payment',
        success_url = "http://localhost:4200/",
        cancel_url = request.build_absolute_uri('/cancel'),
    )
    
    command = Command.objects.create(payment_session = checkout_session.id, address = request.data.get('address'))
    command.save()
    
    for item in items:
        item.command = command
        item.price_on_buying = item.product.price
        if item.product.stock != None:
            item.product.stock -= item.quantity
        item.save()
    

    return Response({'status': "success", 'url': checkout_session.url})


# Create your views here.
@api_view(['POST'])
def webhook(request):
    print(request.data['type'])
    
    if request.data["type"] == "checkout.session.completed":
        command = get_object_or_404(Command, payment_session = request.data["data"]["object"]['id'])
        command.payed = True
        command.save()
        
        items = Item.objects.filter(command = command)
        for item in items:
            item.bought = True
            item.save()
        
        return Response({'status': 'success'})
    
    if request.data["type"] == "checkout.session.expired":
        command = get_object_or_404(Command, payment_session = request.data["data"]["object"]['id'])
        command.cancel()
        
        return Response({'status': 'expired'})
    
    return Response({'status': 'unknown'})