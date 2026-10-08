from django.urls import path
from Shop import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . forms import LoginForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm


urlpatterns = [
    path('', views.ProductView.as_view(), name="home"),
    # path('product-detail/', views.product_detail, name='product-detail'),
    path('product_detail/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.show_cart, name='showcart'),
    path('pluscart/', views.plus_cart),
    path('minuscart/', views.minus_cart),
    path('removecart/', views.remove_cart),
    path('buy/', views.buy_now, name='buy-now'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/', views.address, name='address'),
    path('orders/', views.orders, name='orders'),

    path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name ='Shop/passwordchange.html', form_class=MyPasswordChangeForm, success_url='/passwordchangedone/'), name="passwordchange"),
    path('passwordchangedone/', auth_views.PasswordChangeView.as_view(template_name='Shop/passwordchangedone.html'), name="passwordchangedone"),
    

    path('lehenga/', views.lehenga, name='lehenga'),
    path('lehenga/<slug:data>', views.lehenga, name='lehengaitem'),


    # path('login/', views.login, name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='Shop/login.html', authentication_form = LoginForm), name='login'),



    path('password_reset', auth_views.PasswordResetView.as_view(template_name="Shop/password_reset.html", form_class=MyPasswordResetForm), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='Shop/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='Shop/password_reset_confirm.html', form_class=MySetPasswordForm), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='Shop/password_reset_complete.html'), name='password_reset_complete'),


    path('checkout/', views.checkout, name='checkout'),
    path('paymentdone/', views.payment_done, name='paymentdone'),
    path('registration/', views.CustomerRegistrationView.as_view(), name='customerregistration'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),


    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/fail/', views.payment_fail, name='payment_fail'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),

]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)