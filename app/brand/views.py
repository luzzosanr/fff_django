from django.shortcuts import get_object_or_404
from store.models import Product
from django.template.defaultfilters import slugify
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def catalog(request):
    if not request.user.is_authenticated or not request.user.role == 'BRAND':
        return Response({'status': 'not logged'})
    
    return Response({'status': 'success', 'products': [{'name': item.name, 'price': item.price, 'stock': item.stock, 'slug': item.slug, "description": item.description, "image_url": item.image.url, "is_available": item.is_available, "is_unlimited": item.stock == None} for item in Product.objects.filter(brand = request.user.profile)]})

@api_view(['POST'])
def update_stock(request):
    if not request.user.is_authenticated or not request.user.role == 'BRAND':
        return Response({'status': 'not logged'})
    
    product = get_object_or_404(Product, slug = request.data.get('slug'), brand = request.user.profile, is_available = True)
    
    if request.data.get('stock') == -1:
        stock = None
    else:
        stock = request.data.get('stock')
    product.update_stock(stock)
    
    return Response({'status': 'success'})

@api_view(['POST'])
def update_product(request):
    if not request.user.is_authenticated or not request.user.role == 'BRAND':
        return Response({'status': 'not logged'})
    
    if request.data.get('slug') == '':
        slug = slugify(Product.create(request.data.get('name'), request.user.profile))
    else:
        slug = request.data.get('slug')
        
    
    product = get_object_or_404(Product, slug = slug, brand = request.user.profile)
    
    product.name = request.data.get('name')
    product.price = request.data.get('price')
    product.description = request.data.get('description')
    
    if (product.is_available == False and request.data.get('is_available') == '1'):
        product.activate()
    elif (product.is_available == True and request.data.get('is_available') == '0'):
        product.deactivate()
        
    if (request.data.get('image')):
        product.image = request.data.get('image')
    
    product.save()
    
    return Response({'status': 'success'})
    
    