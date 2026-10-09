from django.contrib import admin

from . models import (
    Customer,
    Product,
    Cart,
    OrderPlaced
)

# Register your models here.
@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display =['id', 'user', 'name', 'division','district','thana','villorroad','zipcode']

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display =['id', 'title','selling_price','discounted_price','description','brand','category','product_image']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','product','quantity']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer','product','quantity','ordered_date','tran_id','status']


# gift card admin
from django.contrib import admin
from .models import GiftCard

@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'user',
        'amount',
        'balance',
        'is_paid',
        'is_active',
        'created_at',
    )
    search_fields = ('code', 'user__username')
    list_filter = ('is_paid', 'is_active')