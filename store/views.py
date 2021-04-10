from django.shortcuts import render, redirect
from .models.product import Product
from django.http import HttpResponse
from .models.catrogry import Cateogrie
from .models.customer import Customer
from django.contrib.auth.hashers import make_password, check_password
from django.views import View
from .models import Orders
from .middlewares.auth import authmiddleware
from django.utils.decorators import method_decorator

class Index(View):
    def get(self, request):
        cart=request.session.get('cart')
        if not cart:
            request.session['cart']={}
        prodd = None
        cateogry = Cateogrie.get_all_cateogries();
        cid = request.GET.get('cateogry')
        if cid:
            prodd = Product.get_all_poduct_byID(cid)
        else:
            prodd = Product.get_all_poduct()
        data = {}
        data['products'] = prodd
        data['cateogry'] = cateogry

        return render(request, 'index.html', data)

    def post(self, request):
        products = request.POST.get('product')
        # print(products)
        remove=request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(products)
            if quantity:
                if remove:
                    if quantity<=1:
                        cart.pop(products)
                    else:
                        cart[products] = quantity -1
                else:
                  cart[products] = quantity + 1
            else:
                cart[products] = 1
        else:
            cart = {}
            cart[products] = 1
        request.session['cart'] = cart
        print(cart)
        return redirect('homepage')


def registerUser(request):
    postData = request.POST
    first_name = postData.get('firstname')
    last_name = postData.get('lastname')
    email = postData.get('email')
    phone = postData.get('phone')
    password = postData.get('password')
    value = {
        'firstname': first_name,
        'lastname': last_name,
        'email': email,
        'phone': phone

    }
    customer = Customer(first_name=first_name, last_name=last_name, phone=phone, email=email, password=password)
    error_message = None
    isExist = customer.exist()
    if isExist:
        error_message = 'Email already registered..'
    elif len(password) < 6:
        error_message = 'password is short...'
    if not error_message:
        customer.password = make_password(customer.password)
        customer.reg()
    else:
        data = {
            'values': value,
            'error': error_message
        }
        return render(request, 'signup.html', data)

    return redirect('homepage')


def signup(request):
    if request.method == "GET":
        return render(request, 'signup.html')
    else:
        return registerUser(request)


class login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_user_by_email(email)
        request.session.clear()
        error = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id
                request.session['email'] = customer.email
                return redirect('homepage')
            else:
                error = 'Email or password invalid'
        else:
            error = 'Email or password invalid'
        return render(request, 'login.html', {'error': error})


def logout(request):
    request.session.clear()
    return redirect('login')



class Cart(View):
    @method_decorator(authmiddleware)
    def get(self, request):
        ids=list(request.session.get('cart').keys())
       # print(list(request.session.get('cart').keys()))
        products=Product.getProductsByID(ids)
        return render(request, 'cart.html',{'products' : products})


class Checkout(View):
    def post(self, request):
        address=request.POST.get('address')
        phone=request.POST.get('phone')
        customer=request.session.get('customer')
        cart=request.session.get('cart')
        products=Product.getProductsByID(list(cart.keys()))

        for product in products:
            order=Orders(customer=Customer(id=customer),
                        product=product,
                        price=product.price,
                        quantity=cart.get(str(product.id)),
                         address=address,
                         phone=phone)
            order.placeOrder()
        request.session['cart']={}


       #print(address,phone,customer)
        return redirect('cart')


class Order(View):
    @method_decorator(authmiddleware)
    def get(self, request):
        customer=request.session.get('customer')
        orders=Orders.get_order_by_customer(customer)
        #print(orders)
        orders=orders.reverse()
        return render(request,'orders.html', {'orders':orders})
