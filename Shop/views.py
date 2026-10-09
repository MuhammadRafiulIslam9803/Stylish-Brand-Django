from django.shortcuts import render, redirect
from .models import Customer, Product, Cart, OrderPlaced
from django.views import View
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from sslcommerz_lib import SSLCOMMERZ
from decimal import Decimal
from django.contrib.auth.models import User

from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
import uuid


# Create your views here.
# def home(request):
#      return render(request, 'Shop/home.html')


class ProductView(View):
    def get(self, request):
        totalitem = 0
        gentspants = Product.objects.filter(category="GP")
        borkhas = Product.objects.filter(category="BK")
        babyfashions = Product.objects.filter(category="BF")
        lehengas = Product.objects.filter(category="L")
        sarees = Product.objects.filter(category="S")
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(
            request,
            "Shop/home.html",
            {
                "gentspants": gentspants,
                "borkhas": borkhas,
                "babyfashions": babyfashions,
                "lehengas": lehengas,
                "sarees": sarees,
                "totalitem": totalitem,
            },
        )


# def product_detail(request):
#  return render(request, 'Shop/productdetail.html')


class ProductDetailView(View):
    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)
            ).exists()
        return render(
            request,
            "Shop/productdetail.html",
            {
                "product": product,
                "item_already_in_cart": item_already_in_cart,
                "totalitem": totalitem,
            },
        )


def add_to_cart(request):
    user = request.user
    product_id = request.GET.get("prod_id")
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect("/cart")


# def show_cart(request):
#  if request.user.is_authenticated:
#   user = request.user
#   cart = Cart.objects.filter(user=user)
#   amount = 0
#   shipping_amount = 100
#   total_amount = 0
#   cart_product = [p for p in Cart.objects.all() if p.user==user]
#   if cart_product:
#    for p in cart_product:
#     tempamount = (p.quantity * p.product.discounted_price)
#     amount += tempamount
#     totalamount = amount+shipping_amount
#   return render(request, 'Shop/addtocart.html', {'carts':cart, 'totalamount':totalamount, 'amount':'amount'})


def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        shipping_amount = 100
        total_amount = 0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount = p.quantity * p.product.discounted_price
                amount += tempamount
                totalamount = amount + shipping_amount
        else:
            return render(request, "shop/emptycart.html")
        return render(
            request,
            "shop/addtocart.html",
            {"carts": cart, "totalamount": totalamount, "amount": amount},
        )


def buy_now(request):
    return render(request, "Shop/buynow.html")


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(
            request, "Shop/profile.html", {"form": form, "active": "btn-primary"}
        )

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data["name"]
            division = form.cleaned_data["division"]
            district = form.cleaned_data["district"]
            thana = form.cleaned_data["thana"]
            villorroad = form.cleaned_data["villorroad"]
            zipcode = form.cleaned_data["zipcode"]
            reg = Customer(
                user=usr,
                name=name,
                division=division,
                district=district,
                thana=thana,
                villorroad=villorroad,
                zipcode=zipcode,
            )
            reg.save()
            messages.success(request, "Congratulations! Profile Updated Successfully")
        return render(
            request, "Shop/profile.html", {"form": form, "active": "btn-primary"}
        )


@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, "Shop/address.html", {"add": add, "active": "btn-primary"})


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, "Shop/orders.html", {"order_placed": op})


# def change_password(request):
#  return render(request, 'Shop/changepassword.html')


def lehenga(request, data=None):
    if data == None:
        lehengas = Product.objects.filter(category="L")
    elif data == "lubnan" or data == "infinity":
        lehengas = Product.objects.filter(category="L").filter(brand=data)
    elif data == "below":
        lehengas = Product.objects.filter(category="L").filter(
            discounted_price__lt=20000
        )
    elif data == "above":
        lehengas = Product.objects.filter(category="L").filter(
            discounted_price__gt=20000
        )
    return render(request, "Shop/lehenga.html", {"lehengas": lehengas})


# def login(request):
#      return render(request, 'Shop/login.html')

# def customerregistration(request):
#  return render(request, 'Shop/customerregistration.html')



class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(
            request,
            "Shop/customerregistration.html",
            {"form": form}
        )

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Congratulations! Registration successfully done."
            )
            return redirect("login")

        return render(
            request,
            "Shop/customerregistration.html",
            {"form": form}
        )


@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0
    shipping_amount = 100
    totalamount = 0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount += tempamount
        totalamount = amount + shipping_amount
    return render(
        request,
        "Shop/checkout.html",
        {"add": add, "totalamount": totalamount, "cart_items": cart_items},
    )


def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()

        amount = 0
        shipping_amount = 100
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount += tempamount
            totalamount = amount + shipping_amount

        data = {"quantity": c.quantity, "amount": amount, "totalamount": totalamount}
        return JsonResponse(data)


def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()

        amount = 0
        shipping_amount = 100
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount += tempamount
            totalamount = amount + shipping_amount

        data = {"quantity": c.quantity, "amount": amount, "totalamount": totalamount}
        return JsonResponse(data)


def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()

        amount = 0
        shipping_amount = 100
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = p.quantity * p.product.discounted_price
            amount += tempamount
            totalamount = amount + shipping_amount

        data = {"amount": amount, "totalamount": totalamount}
        return JsonResponse(data)


@login_required
def initiate_payment(request):
    if request.method == "POST":
        custid = request.POST.get("custid")
        customer = Customer.objects.get(id=custid)
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        # Calculate total
        amount = 0
        shipping_amount = 100
        for item in cart_items:
            amount += item.quantity * item.product.discounted_price
        total_amount = amount + shipping_amount

        # Initialize SSLCommerz session
        settings_dict = {
            "store_id": settings.SSLCZ_STORE_ID,
            "store_pass": settings.SSLCZ_STORE_PASS,
            "issandbox": settings.SSLCZ_IS_SANDBOX,
        }

        sslcz = SSLCOMMERZ(settings_dict)

        post_body = {}
        post_body["total_amount"] = float(total_amount)
        post_body["currency"] = "BDT"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = uuid.uuid4().hex[:4].upper()  # 4-char random for uniqueness
        post_body["tran_id"] = f"ORDER-{user.id}-{customer.id}-{timestamp}-{random_str}"
        # post_body['tran_id'] = f"ORDER_{user.id}_{customer.id}"  # unique transaction id
        post_body["success_url"] = request.build_absolute_uri(
            reverse("payment_success")
        )
        post_body["fail_url"] = request.build_absolute_uri(reverse("payment_fail"))
        post_body["cancel_url"] = request.build_absolute_uri(reverse("payment_cancel"))
        post_body["emi_option"] = 0
        post_body["cus_name"] = customer.name
        post_body["cus_email"] = user.email
        post_body["cus_phone"] = "01711111111"
        post_body["cus_add1"] = customer.villorroad
        post_body["cus_city"] = customer.district
        post_body["cus_country"] = "Bangladesh"
        post_body["shipping_method"] = "NO"
        post_body["num_of_item"] = len(cart_items)
        post_body["product_name"] = "Shopping Cart Items"
        post_body["product_category"] = "General"
        post_body["product_profile"] = "general"

        response = sslcz.createSession(post_body)  # Returns a dict
        print(post_body)

        if response.get("GatewayPageURL"):
            return redirect(response["GatewayPageURL"])
        else:
            return render(request, "Shop/payment_error.html", {"response": response})


@csrf_exempt
def payment_success(request):
    try:
        data = request.POST or request.GET
        tran_id = data.get("tran_id", "")

        if not tran_id:
            messages.error(request, "Transaction ID missing.")
            return redirect("checkout")

        parts = tran_id.split("-")
        if len(parts) < 3:
            messages.error(request, "Invalid transaction ID format.")
            return redirect("checkout")

        user_id = int(parts[1])
        customer_id = int(parts[2])

        user = User.objects.get(id=user_id)
        customer = Customer.objects.get(id=customer_id)

        cart_items = Cart.objects.filter(user=user)
        for item in cart_items:
            # ✅ Save tran_id when creating order
            OrderPlaced.objects.create(
                user=user,
                customer=customer,
                product=item.product,
                quantity=item.quantity,
                tran_id=tran_id,  # <-- Added this line
            )
            item.delete()

        messages.success(request, f"✅ Payment Successful! Transaction ID: {tran_id}")
        return redirect("orders")

    except Exception as e:
        print("❌ Payment success error:", e)
        messages.error(request, "Something went wrong after payment.")
        return redirect("checkout")


# @csrf_exempt
# def payment_success(request):
#     try:
#         data = request.POST or request.GET
#         tran_id = data.get('tran_id', '')

#         if not tran_id:
#             messages.error(request, "Transaction ID missing.")
#             return redirect('checkout')

#         parts = tran_id.split('_')
#         if len(parts) != 3:
#             messages.error(request, "Invalid transaction ID format.")
#             return redirect('checkout')

#         user_id = int(parts[1])
#         customer_id = int(parts[2])

#         user = User.objects.get(id=user_id)
#         customer = Customer.objects.get(id=customer_id)

#         cart_items = Cart.objects.filter(user=user)
#         for item in cart_items:
#             OrderPlaced.objects.create(
#                 user=user,
#                 customer=customer,
#                 product=item.product,
#                 quantity=item.quantity
#             )
#             item.delete()

#         messages.success(request, "✅ Payment Successful! Your order has been placed.")
#         return redirect('orders')

#     except Exception as e:
#         print("❌ Payment success error:", e)
#         messages.error(request, "Something went wrong after payment.")
#         return redirect('checkout')

# def payment_success(request):
#     user = request.user
#     custid = request.GET.get('custid')  # Not sent automatically, optional
#     cart = Cart.objects.filter(user=user)
#     customer = Customer.objects.filter(user=user).first()

#     # Create order entries
#     for c in cart:
#         OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
#         c.delete()

#     messages.success(request, "Payment Successful! Your order has been placed.")
#     return redirect('orders')


# def payment_fail(request):
#     messages.error(request, "Payment Failed! Please try again.")
#     return redirect('checkout')


# def payment_cancel(request):
#     messages.warning(request, "Payment Cancelled!")
#     return redirect('checkout')


@csrf_exempt
def payment_fail(request):
    messages.error(request, "❌ Payment Failed! Please try again.")
    return redirect("checkout")


@csrf_exempt
def payment_cancel(request):
    messages.warning(request, "⚠️ Payment Cancelled by user.")
    return redirect("checkout")


def payment_done(request):
    user = request.user
    custid = request.GET.get("custid")
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(
            user=user, customer=customer, product=c.product, quantity=c.quantity
        ).save()
        c.delete()
    return redirect("orders")
