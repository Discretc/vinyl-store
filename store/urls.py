from django.urls import path
from . import views

urlpatterns = [
    # Home & General
    path('', views.home, name='home'),

    # Authentication
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('vendor/register/', views.vendor_register, name='vendor_register'),
    path('vendor/login/', views.vendor_login, name='vendor_login'),
    path('logout/', views.logout, name='logout'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),

    # Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/item/<int:order_item_id>/cancel/', views.cancel_order_item, name='cancel_order_item'),
    path('orders/item/<int:order_item_id>/refund-request/', views.request_refund, name='request_refund'),

    # Reviews
    path('products/<int:product_id>/review/', views.add_review, name='add_review'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    # Wishlist
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Click History
    path('click-history/', views.view_click_history, name='view_click_history'),

    # Customer Profile
    path('profile/', views.customer_profile, name='customer_profile'),

    # Vendor Dashboard
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/product/add/', views.add_product, name='add_product'),
    path('vendor/product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('vendor/product/<int:product_id>/upload-image/', views.upload_product_image, name='upload_product_image'),
    path('vendor/product/<int:product_id>/toggle-availability/', views.toggle_product_availability, name='toggle_product_availability'),
    path('vendor/image/<int:media_id>/set-primary/', views.set_primary_image, name='set_primary_image'),
    path('vendor/image/<int:media_id>/delete/', views.delete_product_image, name='delete_product_image'),
    path('vendor/product/<int:product_id>/add-promotion/', views.add_promotion, name='add_promotion'),
    path('vendor/promotion/<int:promotion_id>/delete/', views.delete_promotion, name='delete_promotion'),
    path('vendor/promotion/<int:promotion_id>/toggle-status/', views.toggle_promotion_status, name='toggle_promotion_status'),
    path('vendor/orders/', views.vendor_orders, name='vendor_orders'),
    path('vendor/order-item/<int:order_item_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('vendor/refund-request/<int:refund_id>/respond/', views.respond_refund, name='respond_refund'),

    # Shop Pages
    path('shops/<int:store_id>/', views.shop_detail, name='shop_detail'),
    path('vendor/upload-profile/', views.upload_vendor_profile, name='upload_vendor_profile'),
    path('vendor/shop/upload-photo/', views.upload_store_photo, name='upload_store_photo'),
    path('vendor/shop/photo/<int:photo_id>/delete/', views.delete_store_photo, name='delete_store_photo'),

    # Notifications
    path('notifications/', views.notifications_page, name='notifications_page'),
    path('notifications/json/', views.notifications_json, name='notifications_json'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
