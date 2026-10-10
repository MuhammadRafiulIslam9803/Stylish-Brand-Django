import logging
from .decorators import store_admin_required
from django.shortcuts import get_object_or_404
from django.db.models import Q

from django.shortcuts import render, redirect
from .models import Customer, Product, Cart, OrderPlaced, GiftCard
from django.views import View
from .forms import CustomerRegistrationForm, CustomerProfileForm, ProductForm
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

logger = logging.getLogger(__name__)

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

@login_required
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


# for all cetagory filtering by brand and price range


def category_products(request, category_code, data=None):
    category_info = {
        "S": {
            "title": "Saree Collection",
            "brands": ["Rang", "Aarong", "Kay Kraft"],
            "all_url": "saree",
            "item_url": "sareeitem",
        },
        "GP": {
            "title": "Gents Pant Collection",
            "brands": ["Yellow", "Apex", "Ecstasy", "Sailor"],
            "all_url": "gents-pant",
            "item_url": "gentspantitem",
        },
        "BK": {
            "title": "Borkha Collection",
            "brands": ["Aarong", "Rang", "Kay Kraft"],
            "all_url": "borkha",
            "item_url": "borkhaitem",
        },
        "BF": {
            "title": "Baby Fashion Collection",
            "brands": ["Rang", "Kay Kraft", "Aarong", "Sailor"],
            "all_url": "baby-fashion",
            "item_url": "babyfashionitem",
        },
    }

    info = category_info[category_code]

    products = Product.objects.filter(category=category_code)

    if data == "below":
        products = products.filter(discounted_price__lt=20000)

    elif data == "above":
        products = products.filter(discounted_price__gt=20000)

    elif data is not None:
        if data not in info["brands"]:
            products = Product.objects.none()
        else:
            products = products.filter(brand=data)

    return render(
        request,
        "Shop/category_products.html",
        {
            "products": products,
            "category_title": info["title"],
            "brands": info["brands"],
            "category_url_name": info["all_url"],
            "item_url_name": info["item_url"],
            "selected_filter": data,
        },
    )


def saree(request, data=None):
    return category_products(request, "S", data)


def gents_pant(request, data=None):
    return category_products(request, "GP", data)


def borkha(request, data=None):
    return category_products(request, "BK", data)


def baby_fashion(request, data=None):
    return category_products(request, "BF", data)


# def change_password(request):
#  return render(request, 'Shop/changepassword.html')

# for lehenga filtering

# def lehenga(request, data=None):
#     if data == None:
#         lehengas = Product.objects.filter(category="L")
#     elif data == "lubnan" or data == "infinity":
#         lehengas = Product.objects.filter(category="L").filter(brand=data)
#     elif data == "below":
#         lehengas = Product.objects.filter(category="L").filter(
#             discounted_price__lt=20000
#         )
#     elif data == "above":
#         lehengas = Product.objects.filter(category="L").filter(
#             discounted_price__gt=20000
#         )
#     return render(request, "Shop/lehenga.html", {"lehengas": lehengas})


def lehenga(request, data=None):

    if data is None:
        lehengas = Product.objects.filter(category="L")

    elif data in ["Rang", "Sailor", "Kay Kraft", "Yellow"]:
        lehengas = Product.objects.filter(category="L", brand=data)

    elif data == "below":
        lehengas = Product.objects.filter(category="L", discounted_price__lt=20000)

    elif data == "above":
        lehengas = Product.objects.filter(category="L", discounted_price__gt=20000)

    else:
        lehengas = Product.objects.none()

    return render(request, "Shop/lehenga.html", {"lehengas": lehengas})


# def login(request):
#      return render(request, 'Shop/login.html')

# def customerregistration(request):
#  return render(request, 'Shop/customerregistration.html')


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "Shop/customerregistration.html", {"form": form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request, "Congratulations! Registration successfully done."
            )
            return redirect("login")

        return render(request, "Shop/customerregistration.html", {"form": form})


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
        # custid = request.POST.get("custid")
        # customer = Customer.objects.get(id=custid)
        # user = request.user
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        custid = request.POST.get("custid")

        # handle error when adress is missing 
        try:
            if custid:
                customer = Customer.objects.get(
                    id=custid,
                    user=user
                )
            else:
                customer = Customer.objects.get(user=user)

        except Customer.DoesNotExist:
            messages.warning(
                request,
                "Please complete your profile and address before payment."
            )
            return redirect("profile")
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


# gift card
@login_required
def gift_card_page(request):
    gift_amounts = [500, 1000, 2000]

    return render(
        request,
        "Shop/gift_card.html",
        {"gift_amounts": gift_amounts},
    )


@login_required
def gift_card_buy(request):
    if request.method != "POST":
        return render_gift_card_error(
            request,
            "Invalid Request",
            "Gift Card purchase must be submitted using the checkout form.",
            "INVALID_REQUEST",
        )

    try:
        amount = Decimal(request.POST.get("amount", "0"))

        if amount not in [
            Decimal("500"),
            Decimal("1000"),
            Decimal("2000"),
        ]:
            return render_gift_card_error(
                request,
                "Invalid Gift Card Amount",
                "Please select one of the available amounts: ৳500, ৳1000, or ৳2000.",
                "INVALID_AMOUNT",
            )

        customer = Customer.objects.filter(user=request.user).first()

        if not customer:
            return render_gift_card_error(
                request,
                "Customer Profile Missing",
                "Please complete your customer profile before purchasing a Gift Card.",
                "PROFILE_MISSING",
            )

        settings_dict = {
            "store_id": settings.SSLCZ_STORE_ID,
            "store_pass": settings.SSLCZ_STORE_PASS,
            "issandbox": settings.SSLCZ_IS_SANDBOX,
        }

        sslcz = SSLCOMMERZ(settings_dict)

        tran_id = f"GIFT-{request.user.id}-{uuid.uuid4().hex[:12].upper()}"

        post_body = {
            "total_amount": float(amount),
            "currency": "BDT",
            "tran_id": tran_id,
            "success_url": request.build_absolute_uri(
                reverse("gift_card_payment_success")
            ),
            "fail_url": request.build_absolute_uri(reverse("gift_card_payment_fail")),
            "cancel_url": request.build_absolute_uri(
                reverse("gift_card_payment_cancel")
            ),
            "emi_option": 0,
            "cus_name": customer.name,
            "cus_email": request.user.email or "customer@example.com",
            "cus_phone": "01711111111",
            "cus_add1": customer.villorroad,
            "cus_city": customer.district,
            "cus_country": "Bangladesh",
            "shipping_method": "NO",
            "num_of_item": 1,
            "product_name": "Gift Card",
            "product_category": "Gift Card",
            "product_profile": "general",
        }

        pending_code = f"PENDING-{uuid.uuid4().hex[:12].upper()}"

        gift_card = GiftCard.objects.create(
            user=request.user,
            code=pending_code,
            amount=amount,
            balance=amount,
            is_paid=False,
            is_active=False,
            tran_id=tran_id,
        )

        response = sslcz.createSession(post_body)

        if response.get("GatewayPageURL"):
            return redirect(response["GatewayPageURL"])

        return render_gift_card_error(
            request,
            "Payment Session Failed",
            "The payment gateway did not provide a checkout URL. Your Gift Card remains inactive.",
            "SESSION_CREATION_FAILED",
            tran_id,
        )

    except (ValueError, TypeError, ArithmeticError):
        return render_gift_card_error(
            request,
            "Invalid Gift Card Amount",
            "The selected amount could not be processed. Please choose a valid Gift Card amount.",
            "INVALID_AMOUNT",
        )

    except Exception:
        logger.exception("Gift Card checkout session creation failed")

        return render_gift_card_error(
            request,
            "Payment Processing Error",
            "An unexpected error occurred while starting checkout. Check the payment status before trying again.",
            "CHECKOUT_ERROR",
        )


@csrf_exempt
def gift_card_payment_success(request):
    val_id = request.POST.get("val_id") or request.GET.get("val_id")
    callback_tran_id = request.POST.get("tran_id") or request.GET.get("tran_id")

    if not val_id or not callback_tran_id:
        return render_gift_card_error(
            request,
            "Payment Information Missing",
            "The payment gateway did not return the required validation ID or transaction ID. Payment status could not be verified.",
            "MISSING_PAYMENT_DATA",
            callback_tran_id,
        )

    try:
        gift_card = GiftCard.objects.get(tran_id=callback_tran_id)

        if gift_card.is_paid and gift_card.is_active:
            return render(
                request,
                "Shop/gift_card_success.html",
                {"gift_card": gift_card},
            )

        settings_dict = {
            "store_id": settings.SSLCZ_STORE_ID,
            "store_pass": settings.SSLCZ_STORE_PASS,
            "issandbox": settings.SSLCZ_IS_SANDBOX,
        }

        sslcz = SSLCOMMERZ(settings_dict)
        validation = sslcz.validationTransactionOrder(val_id)

        status = validation.get("status")
        verified_tran_id = validation.get("tran_id")
        verified_amount = Decimal(str(validation.get("amount", "0")))

        if status not in ["VALID", "VALIDATED"]:
            return render_gift_card_error(
                request,
                "Payment Verification Failed",
                "The payment gateway did not confirm a valid transaction. Your Gift Card remains inactive.",
                "INVALID_PAYMENT_STATUS",
                callback_tran_id,
            )

        if verified_tran_id != gift_card.tran_id:
            return render_gift_card_error(
                request,
                "Transaction ID Mismatch",
                "The transaction ID returned by the gateway does not match the Gift Card purchase. The card has not been activated.",
                "TRANSACTION_MISMATCH",
                callback_tran_id,
            )

        if verified_amount != gift_card.amount:
            return render_gift_card_error(
                request,
                "Payment Amount Mismatch",
                "The amount confirmed by the payment gateway does not match the Gift Card amount. The card has not been activated.",
                "AMOUNT_MISMATCH",
                callback_tran_id,
            )

        gift_card.code = f"GIFT-{uuid.uuid4().hex[:12].upper()}"
        gift_card.is_paid = True
        gift_card.is_active = True
        gift_card.balance = gift_card.amount

        gift_card.save(
            update_fields=[
                "code",
                "is_paid",
                "is_active",
                "balance",
            ]
        )

        return render(
            request,
            "Shop/gift_card_success.html",
            {"gift_card": gift_card},
        )

    except GiftCard.DoesNotExist:
        return render_gift_card_error(
            request,
            "Gift Card Transaction Not Found",
            "No pending Gift Card matches this transaction ID. The payment could not be linked to a Gift Card.",
            "GIFT_CARD_NOT_FOUND",
            callback_tran_id,
        )

    except Exception:
        logger.exception("Gift Card payment verification failed")

        return render_gift_card_error(
            request,
            "Payment Verification Error",
            "An unexpected error occurred while verifying the payment. Your Gift Card has not been activated by this error handler. Check the server log and confirm payment status before retrying.",
            "VERIFICATION_ERROR",
            callback_tran_id,
        )


def render_gift_card_error(
    request,
    title,
    message,
    error_code="GIFT_CARD_ERROR",
    transaction_id=None,
):
    return render(
        request,
        "Shop/gift_card_error.html",
        {
            "error_title": title,
            "error_message": message,
            "error_code": error_code,
            "transaction_id": transaction_id,
        },
    )


@csrf_exempt
def gift_card_payment_fail(request):
    tran_id = request.POST.get("tran_id") or request.GET.get("tran_id")

    return render_gift_card_error(
        request,
        "Gift Card Payment Failed",
        "The payment gateway returned a failed payment result. Your Gift Card has not been activated. If money was deducted, confirm the transaction status before trying again.",
        "PAYMENT_FAILED",
        tran_id,
    )


@csrf_exempt
def gift_card_payment_cancel(request):
    tran_id = request.POST.get("tran_id") or request.GET.get("tran_id")

    return render_gift_card_error(
        request,
        "Payment Cancelled",
        "The Gift Card payment process was cancelled. No Gift Card was activated by this cancellation response.",
        "PAYMENT_CANCELLED",
        tran_id,
    )




# stored admin 



@login_required
@store_admin_required
def store_admin_dashboard(request):
    context = {
        "total_products": Product.objects.count(),
        "total_customers": Customer.objects.count(),
        "total_orders": OrderPlaced.objects.count(),
    }

    return render(
        request,
        "Shop/admin_dashboard.html",
        context,
    )

# Product Management - Store Admin




@login_required
@store_admin_required
def admin_product_list(request):
    products = Product.objects.all().order_by("-id")

    search_query = request.GET.get("q", "").strip()

    if search_query:
        products = products.filter(
            Q(title__icontains=search_query)
            | Q(brand__icontains=search_query)
        )

    context = {
        "products": products,
        "search_query": search_query,
    }

    return render(request, "Shop/admin_product_list.html", context)


@login_required
@store_admin_required
def admin_product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect("admin_product_list")
    else:
        form = ProductForm()

    return render(
        request,
        "Shop/admin_product_form.html",
        {
            "form": form,
            "page_title": "Add New Product",
            "button_text": "Add Product",
        },
    )


@login_required
@store_admin_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect("admin_product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "Shop/admin_product_form.html",
        {
            "form": form,
            "page_title": "Edit Product",
            "button_text": "Save Changes",
            "product": product,
        },
    )


@login_required
@store_admin_required
def admin_product_delete(request, pk):
    if request.method != "POST":
        return redirect("admin_product_list")

    product = get_object_or_404(Product, pk=pk)
    product.delete()

    messages.success(request, "Product deleted successfully!")
    return redirect("admin_product_list")

# admin order list management

@login_required
@store_admin_required
def admin_order_list(request):
    orders = OrderPlaced.objects.select_related(
        "user", "customer", "product"
    ).all().order_by("-ordered_date")

    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if search_query:
        orders = orders.filter(
            Q(customer__name__icontains=search_query)
            | Q(product__title__icontains=search_query)
            | Q(tran_id__icontains=search_query)
            | Q(user__username__icontains=search_query)
        )

    allowed_statuses = dict(
        OrderPlaced._meta.get_field("status").choices
    )

    if status_filter in allowed_statuses:
        orders = orders.filter(status=status_filter)

    context = {
        "orders": orders,
        "search_query": search_query,
        "status_filter": status_filter,
        "status_choices": OrderPlaced._meta.get_field("status").choices,
    }

    return render(request, "Shop/admin_order_list.html", context)


@login_required
@store_admin_required
def admin_order_update_status(request, pk):
    if request.method != "POST":
        return redirect("admin_order_list")

    order = get_object_or_404(OrderPlaced, pk=pk)

    new_status = request.POST.get("status", "").strip()

    allowed_statuses = dict(
        OrderPlaced._meta.get_field("status").choices
    )

    if new_status not in allowed_statuses:
        messages.error(request, "Invalid order status.")
        return redirect("admin_order_list")

    order.status = new_status
    order.save(update_fields=["status"])

    messages.success(
        request,
        f"Order #{order.pk} status updated to {new_status}."
    )

    return redirect("admin_order_list")

# admin customer list management

@login_required
@store_admin_required
def admin_customer_list(request):
    customers = Customer.objects.select_related(
        "user"
    ).all().order_by("-id")

    search_query = request.GET.get("q", "").strip()

    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query)
            | Q(user__username__icontains=search_query)
            | Q(district__icontains=search_query)
            | Q(thana__icontains=search_query)
            | Q(division__icontains=search_query)
            | Q(villorroad__icontains=search_query)
        )

    return render(request, "Shop/admin_customer_list.html", {
        "customers": customers,
        "search_query": search_query,
    })


@login_required
@store_admin_required
def admin_customer_orders(request, pk):
    customer = get_object_or_404(
        Customer.objects.select_related("user"),
        pk=pk,
    )

    orders = OrderPlaced.objects.filter(
        customer=customer
    ).select_related("product", "user").order_by("-ordered_date")

    return render(request, "Shop/admin_customer_orders.html", {
        "customer": customer,
        "orders": orders,
    })