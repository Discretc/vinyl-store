from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# ======================= CUSTOMER MODEL =======================
class Customer(models.Model):
    """
    Represents a customer who can browse and purchase vinyl records.
    Email is unique to allow login identification.
    """
    customerID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Will store hashed password
    phoneNumber = models.CharField(max_length=20, blank=True)
    shippingAddress = models.TextField(blank=True)
    createdTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customer'

    def set_password(self, raw_password):
        """Hash and set the password."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if provided password matches the hashed password."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.firstName} {self.lastName} ({self.email})"


# ======================= VENDOR MODEL =======================
class Vendor(models.Model):
    """
    Represents a vendor who can create stores and sell vinyl records.
    Email is unique to allow login identification.
    """
    vendorID = models.AutoField(primary_key=True)
    vendorName = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Will store hashed password
    phoneNumber = models.CharField(max_length=20, blank=True)
    profileImage = models.ImageField(upload_to='vendor_profiles/', null=True, blank=True)
    createdTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendor'

    def set_password(self, raw_password):
        """Hash and set the password."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if provided password matches the hashed password."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.vendorName


# ======================= STORE MODEL =======================
class Store(models.Model):
    """
    Represents a vendor's store - one vendor can have one store.
    Contains store information and links to the vendor.
    """
    storeID = models.AutoField(primary_key=True)
    vendorID = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='store')
    storeName = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    createdTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store'

    def __str__(self):
        return self.storeName


# ======================= PRODUCT MODEL =======================
class Product(models.Model):
    """
    Represents a vinyl record product in a store.
    Tracks inventory and pricing information.
    """
    productID = models.AutoField(primary_key=True)
    storeID = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    productName = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stockQuantity = models.IntegerField(validators=[MinValueValidator(0)])
    availability = models.BooleanField(default=True)
    createdTime = models.DateTimeField(auto_now_add=True)
    updatedTime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return self.productName

    def is_in_stock(self):
        """Check if product has inventory."""
        return self.stockQuantity > 0


# ======================= PRODUCT MEDIA MODEL =======================
class ProductMedia(models.Model):
    """
    Stores media (images) for products.
    Each product can have multiple images with sorting order.
    isPrimary indicates the main product image.
    """
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    mediaID = models.AutoField(primary_key=True)
    productID = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media')
    mediaURL = models.ImageField(upload_to='product_images/')
    mediaType = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image')
    isPrimary = models.BooleanField(default=False)
    sortedOrder = models.IntegerField(default=0)

    class Meta:
        db_table = 'product_media'
        ordering = ['sortedOrder']

    def __str__(self):
        return f"{self.productID.productName} - Media {self.mediaID}"


# ======================= CART ITEM MODEL =======================
class CartItem(models.Model):
    """
    Represents items in a customer's shopping cart.
    Composite key (customerID, productID) - each product appears once per cart.
    """
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart_items')
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    addedTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_item'
        unique_together = ('customerID', 'productID')

    def __str__(self):
        return f"Cart: {self.customerID} - {self.productID.productName} (qty: {self.quantity})"


# ======================= ORDER MODEL =======================
class Order(models.Model):
    """
    Represents a customer's order containing one or more items.
    Tracks order date and shipping information.
    """
    orderID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    orderDate = models.DateTimeField(auto_now_add=True)
    shippingAddress = models.TextField()
    totalAmount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'order'

    def __str__(self):
        return f"Order #{self.orderID} by {self.customerID}"


# ======================= ORDER ITEM MODEL =======================
class OrderItem(models.Model):
    """
    Represents individual items within an order.
    Stores the price at time of purchase (paidPrice) for historical accuracy.
    """
    orderItemID = models.AutoField(primary_key=True)
    orderID = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    productID = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    paidPrice = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'order_item'

    def __str__(self):
        return f"OrderItem #{self.orderItemID} - {self.productID.productName}"


# ======================= ORDER STATUS MODEL =======================
class OrderStatus(models.Model):
    """
    Tracks the status of each order item through its lifecycle.
    Multiple status records can exist per order item (history tracking).
    """
    STATUS_CHOICES = [
        ('Processing', 'Processing'),
        ('Holding', 'Holding'),
        ('Shipping', 'Shipping'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    statusID = models.AutoField(primary_key=True)
    orderItemID = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')
    updatedDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_status'

    def __str__(self):
        return f"Order Item #{self.orderItemID.orderItemID} - {self.status}"


# ======================= CANCELLED ITEM MODEL =======================
class CancelledItem(models.Model):
    """
    Stores cancellation information for order items.
    Links to OrderStatus via statusID (one-to-one relationship).
    """
    CANCELLATION_REASONS = [
        ('out_of_stock', 'Out of Stock'),
        ('customer_request', 'Customer Request'),
        ('damaged_item', 'Damaged Item'),
        ('payment_failed', 'Payment Failed'),
        ('other', 'Other'),
    ]

    statusID = models.OneToOneField(OrderStatus, on_delete=models.CASCADE, primary_key=True, related_name='cancelled_item')
    cancelledReason = models.CharField(max_length=50, choices=CANCELLATION_REASONS)

    class Meta:
        db_table = 'cancelled_item'

    def __str__(self):
        return f"Cancelled - {self.get_cancelledReason_display()}"


# ======================= WISHLIST ITEM MODEL =======================
class WishlistItem(models.Model):
    """
    Stores items in a customer's wishlist.
    Tracks original price and discount at time of adding.
    """
    wishlistItemID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='wishlist_items')
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    addedDate = models.DateTimeField(auto_now_add=True)
    originalPrice = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discountRate = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    priceAtAddedTime = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'wishlist_item'
        unique_together = ('customerID', 'productID')

    def __str__(self):
        return f"Wishlist: {self.customerID} - {self.productID.productName}"


# ======================= PROMOTION MODEL =======================
class Promotion(models.Model):
    """
    Represents a discount promotion applied to a product.
    Discount is applied if current date is within startDate and endDate.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
    ]

    promotionID = models.AutoField(primary_key=True)
    productID = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='promotions')
    discountRate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    createdTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'promotion'

    def __str__(self):
        return f"Promo: {self.productID.productName} - {self.discountRate}% off"

    def is_active(self):
        """Check if promotion is currently active."""
        now = timezone.now()
        return self.startDate <= now <= self.endDate and self.status == 'active'

    def get_discount_amount(self, price):
        """Calculate discount amount for given price."""
        if self.is_active():
            return price * (self.discountRate / 100)
        return 0


# ======================= REVIEW MODEL =======================
class Review(models.Model):
    """
    Stores customer reviews and ratings for products.
    Rating is 1-5 stars. Comment is optional.
    """
    reviewID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews')
    productID = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    createdDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review'
        unique_together = ('customerID', 'productID')

    def __str__(self):
        return f"Review by {self.customerID} for {self.productID} - {self.rating}★"


# ======================= CLICK HISTORY MODEL =======================
class ClickHistory(models.Model):
    """
    Tracks product views by customers for analytics.
    Records when a customer viewed a product.
    """
    historyID = models.AutoField(primary_key=True)
    customerID = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='click_history')
    productID = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewedDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'click_history'

    def __str__(self):
        return f"{self.customerID} viewed {self.productID} on {self.viewedDate}"
