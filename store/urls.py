from .views import Index, signup, login, logout, Cart,Checkout,Order
from django.urls import path

urlpatterns = [
    path('', Index.as_view(), name='homepage'),
    path('signup', signup),
    path('login', login.as_view(), name='login'),
    path('logout', logout, name='logout'),
    path('cart', Cart.as_view(), name='cart'),
    path('checkout',Checkout.as_view(),name='checkout'),
    path('orders/',Order.as_view(),name='checkout')

]
