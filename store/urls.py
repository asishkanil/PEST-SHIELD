from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from django.urls import path
from . import views
from django.shortcuts import redirect


urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("detect/", views.detect_pest, name="detect_pest"),
    path("shop/", views.shop, name="shop"),
    path("cart/", views.cart, name="cart"),  # <---- Ensure this is here
    path("add-to-cart/<int:pesticide_id>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update-cart-item/<int:cart_item_id>/", views.update_cart_item, name="update_cart_item"),
    path("order-confirmation/", views.order_confirmation, name="order_confirmation"),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("manage-stock/", views.manage_stock, name="manage_stock"),
    path("admin/update-order/<int:order_id>/", views.update_order_status, name="update_order_status"),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('update-order/<int:order_id>/', views.update_order_status, name='update_order_status'),  
      path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('order-success/', views.order_success, name='order_success'),
    path('add_pesticide/', views.add_pesticide, name='add_pesticide')




]


