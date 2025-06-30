from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop_view, name='shop'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),  
    path('cart/', views.cart_view, name='cart'),  
    path('update-cart/', views.update_cart, name='update_cart'),
]
