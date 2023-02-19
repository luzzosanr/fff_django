from django.urls import path
from . import views

# url starts with /api/admin/brand/
urlpatterns = [
    path('catalog', views.catalog, name = 'catalog_admin'),
    path('update/stock', views.update_stock, name = 'update_stock'),
    path('update/product', views.update_product, name = 'update_product'),
]