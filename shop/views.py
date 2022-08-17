from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from . import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']
    return {'cartItems':cartItems, 'items':items, 'order':order}


def index(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()

    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    cart_items_count = 0
    for i in cart:
        cart_items_count += cart[i]["quantity"]
    
    return render(request, "index.html", {'products':products, 'cartItems': cartItems, 'cart_items_count': cart_items_count})

def cart(request):
    data = cartData(request)
    items = []
    order = []
    cartItems = data['cartItems']
    cart_total = 0.0
    cart_items_count = 0
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    for i in cart:
        try:
            cartItems += cart[i]["quantity"]
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])
            cart_total += total
            cart_items_count += cart[i]["quantity"]

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'image':product.image,
                },
                'quantity':cart[i]["quantity"],
                'get_total':total
            }
            items.append(item)
        except:
            pass
    return render(request, "cart.html", {'items':items, 'order':order, 'cartItems':cartItems, 'cart_total': cart_total, 'cart_items_count': cart_items_count})

def convertCartToDB(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    for i in cart:
        product = Product.objects.get(id=i)
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        update_order, created = UpdateOrder.objects.get_or_create(order_id=order, desc="Your Order is Successfully Placed.")

        orderItem.quantity = cart[i]["quantity"]
        orderItem.save()
        update_order.save()

def checkout(request):
    convertCartToDB(request)
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data["cartItems"]
    total = order.get_cart_total
    customer = request.user.customer
    unavailable_messages = []
    for item in items:
        if item.product.qty == 0:
            unavailable_messages.append("I'm Sorry but we are out of stock for "+item.product.name)
        elif item.quantity > item.product.qty:
            unavailable_messages.append("I'm Sorry but we only have "+str(item.product.qty)+"kg of "+item.product.name)
    if len(unavailable_messages) > 0:
        return render(request,"cart.html",{'items':items, 'order':order, 'cartItems':cartItems,'cart_total': total, 'cart_items_count': cartItems,"unavailable_messages":unavailable_messages} ) 
    if request.method == "POST":
        payment = request.POST['payment']
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        id = order.id  
        alert = True
        return render(request, "checkout.html", {'alert':alert, 'id':id})
    return render(request, "checkout.html", {'items':items, 'order':order, 'cartItems':cartItems, 'cart_total': total, 'cart_items_count': cartItems})


def updateItem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productID)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    update_order, created = UpdateOrder.objects.get_or_create(order_id=order, desc="Your Order is Successfully Placed.")

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == 'empty':
        orderItem.quantity = 0
        orderItem.delete()

    orderItem.save()
    update_order.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)

def product_view(request, myid):
    product = Product.objects.filter(id=myid).first()
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    if request.method=="POST":
        content = request.POST['content']
        return redirect(f"/product_view/{product.id}")
    return render(request, "product_view.html", {'product':product, 'cartItems':cartItems})


def change_password(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(current_password):
                u.set_password(new_password)
                u.save()
                alert = True
                return render(request, "change_password.html", {'alert':alert})
            else:
                currpasswrong = True
                return render(request, "change_password.html", {'currpasswrong':currpasswrong})
        except:
            pass
    return render(request, "change_password.html", {'cartItems':cartItems})


def register(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=="POST":   
            username = request.POST.get('username')
            full_name=request.POST.get('full_name')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')

            if password1 != password2:
                alert = True
                return render(request, "register.html", {'alert':alert})

            if User.objects.filter(username = username).first():
                messages.error(request, "This username is already taken")
                return redirect('/')

            user = User.objects.create_user(username=username, password=password1, email=email)
            customers = Customer.objects.create(user=user, name=full_name, phone_number=phone_number, email=email)
            user.save()
            customers.save()
            return render(request, "login.html")
    return render(request, "register.html")


def Login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                alert = True
                return render(request, "login.html", {"alert":alert})
    return render(request, "login.html")


def Logout(request):
    logout(request)
    alert = True
    return render(request, "index.html", {'alert':alert})

def adminclick_view(request):
    return HttpResponseRedirect('adminlogin')

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount= Customer.objects.all().count()
    productcount=Product.objects.all().count()
    ordercount=Order.objects.all().count()

    mydict={
    'customercount':customercount,
    'productcount':productcount,
    'ordercount':ordercount,
    # 'data':zip(ordered_products,ordered_bys,orders),
    }
    return render(request,'admin_dashboard_cards.html',context=mydict)


@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=Product.objects.all()
    return render(request,'admin_products.html',{'products':products})


@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'admin_add_products.html',{'productForm':productForm})

@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')

@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'admin_update_product.html',{'productForm':productForm})

