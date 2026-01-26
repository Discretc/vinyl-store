from django.contrib import admin
from .models import (
    Customer, Vendor, Store, Product, ProductMedia, CartItem, Order, OrderItem,
    OrderStatus, CancelledItem, WishlistItem, Promotion, Review, ClickHistory
)


# ======================= CUSTOMER ADMIN =======================
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customerID', 'firstName', 'lastName', 'email', 'phoneNumber', 'createdTime')
    search_fields = ('email', 'firstName', 'lastName')
    readonly_fields = ('createdTime',)
    list_filter = ('createdTime',)


# ======================= VENDOR ADMIN =======================
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendorID', 'vendorName', 'email', 'phoneNumber', 'createdTime')
    search_fields = ('email', 'vendorName')
    readonly_fields = ('createdTime',)
    list_filter = ('createdTime',)


# ======================= STORE ADMIN =======================
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('storeID', 'storeName', 'vendorID', 'createdTime')
    search_fields = ('storeName', 'vendorID__vendorName')
    readonly_fields = ('createdTime',)
    list_filter = ('createdTime',)


# ======================= PRODUCT MEDIA INLINE =======================
class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1
    fields = ('mediaURL', 'mediaType', 'isPrimary', 'sortedOrder')


# ======================= PRODUCT ADMIN =======================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('productID', 'productName', 'storeID', 'price', 'stockQuantity', 'availability', 'createdTime')
    search_fields = ('productName', 'storeID__storeName')
    list_filter = ('availability', 'createdTime')
    readonly_fields = ('createdTime', 'updatedTime')
    inlines = [ProductMediaInline]


# ======================= PRODUCT MEDIA ADMIN =======================
@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ('mediaID', 'productID', 'mediaType', 'isPrimary', 'sortedOrder')
    list_filter = ('mediaType', 'isPrimary')
    search_fields = ('productID__productName',)


# ======================= CART ITEM ADMIN =======================
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('customerID', 'productID', 'quantity', 'addedTime')
    search_fields = ('customerID__email', 'productID__productName')
    list_filter = ('addedTime',)


# ======================= ORDER ITEM INLINE =======================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('productID', 'quantity', 'paidPrice')
    readonly_fields = ('productID', 'quantity', 'paidPrice')
    can_delete = False


# ======================= ORDER ADMIN =======================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderID', 'customerID', 'orderDate', 'totalAmount')
    search_fields = ('customerID__email', 'orderID')
    list_filter = ('orderDate',)
    readonly_fields = ('orderDate',)
    inlines = [OrderItemInline]


# ======================= ORDER ITEM ADMIN =======================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('orderItemID', 'orderID', 'productID', 'quantity', 'paidPrice')
    search_fields = ('orderID__orderID', 'productID__productName')
    readonly_fields = ('orderID', 'productID', 'quantity', 'paidPrice')


# ======================= ORDER STATUS ADMIN =======================
@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('statusID', 'orderItemID', 'status', 'updatedDate')
    list_filter = ('status', 'updatedDate')
    search_fields = ('orderItemID__orderID__orderID',)
    readonly_fields = ('updatedDate',)


# ======================= CANCELLED ITEM ADMIN =======================
@admin.register(CancelledItem)
class CancelledItemAdmin(admin.ModelAdmin):
    list_display = ('statusID', 'cancelledReason')
    list_filter = ('cancelledReason',)
    search_fields = ('statusID__orderItemID__orderID__orderID',)


# ======================= WISHLIST ITEM ADMIN =======================
@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('wishlistItemID', 'customerID', 'productID', 'priceAtAddedTime', 'addedDate')
    search_fields = ('customerID__email', 'productID__productName')
    list_filter = ('addedDate',)
    readonly_fields = ('addedDate',)


# ======================= PROMOTION ADMIN =======================
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('promotionID', 'productID', 'discountRate', 'startDate', 'endDate', 'status')
    list_filter = ('status', 'startDate', 'endDate')
    search_fields = ('productID__productName',)


# ======================= REVIEW ADMIN =======================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewID', 'customerID', 'productID', 'rating', 'createdDate')
    search_fields = ('customerID__email', 'productID__productName')
    list_filter = ('rating', 'createdDate')
    readonly_fields = ('createdDate',)


# ======================= CLICK HISTORY ADMIN =======================
@admin.register(ClickHistory)
class ClickHistoryAdmin(admin.ModelAdmin):
    list_display = ('historyID', 'customerID', 'productID', 'viewedDate')
    search_fields = ('customerID__email', 'productID__productName')
    list_filter = ('viewedDate',)
    readonly_fields = ('viewedDate',)
