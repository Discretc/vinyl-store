from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Avg
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from decimal import Decimal
import json

from .models import (
    Customer, Vendor, Store, Product, ProductMedia, CartItem, Order, OrderItem,
    OrderStatus, Review, WishlistItem, Promotion, ClickHistory
)


# ======================= AUTHENTICATION VIEWS =======================

def customer_register(request):
    """Register a new customer account."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        # Validation
        errors = []
        if not first_name or not last_name:
            errors.append("First name and last name are required.")
        if not email:
            errors.append("Email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if Customer.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'store/customer_register.html')

        # Create customer
        customer = Customer(
            firstName=first_name,
            lastName=last_name,
            email=email,
            phoneNumber=phone,
            shippingAddress=address
        )
        customer.set_password(password)
        customer.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('customer_login')

    return render(request, 'store/customer_register.html')


def customer_login(request):
    """Login for customers."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        try:
            customer = Customer.objects.get(email=email)
            if customer.check_password(password):
                request.session['customer_id'] = customer.customerID
                request.session['customer_name'] = f"{customer.firstName} {customer.lastName}"
                request.session['user_type'] = 'customer'
                messages.success(request, f"Welcome back, {customer.firstName}!")
                return redirect('product_list')
            else:
                messages.error(request, "Invalid password.")
        except Customer.DoesNotExist:
            messages.error(request, "Email not found.")

    return render(request, 'store/customer_login.html')


def vendor_register(request):
    """Register a new vendor account."""
    if request.method == 'POST':
        vendor_name = request.POST.get('vendor_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        phone = request.POST.get('phone', '').strip()
        store_name = request.POST.get('store_name', '').strip()
        store_desc = request.POST.get('store_description', '').strip()

        # Validation
        errors = []
        if not vendor_name or not store_name:
            errors.append("Vendor name and store name are required.")
        if not email:
            errors.append("Email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if Vendor.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'store/vendor_register.html')

        # Create vendor and store
        vendor = Vendor(
            vendorName=vendor_name,
            email=email,
            phoneNumber=phone
        )
        vendor.set_password(password)
        vendor.save()

        # Create associated store
        Store.objects.create(
            vendorID=vendor,
            storeName=store_name,
            description=store_desc
        )

        messages.success(request, "Vendor account created! Please log in.")
        return redirect('vendor_login')

    return render(request, 'store/vendor_register.html')


def vendor_login(request):
    """Login for vendors."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        try:
            vendor = Vendor.objects.get(email=email)
            if vendor.check_password(password):
                request.session['vendor_id'] = vendor.vendorID
                request.session['vendor_name'] = vendor.vendorName
                request.session['user_type'] = 'vendor'
                messages.success(request, f"Welcome, {vendor.vendorName}!")
                return redirect('vendor_dashboard')
            else:
                messages.error(request, "Invalid password.")
        except Vendor.DoesNotExist:
            messages.error(request, "Email not found.")

    return render(request, 'store/vendor_login.html')


def logout(request):
    """Logout user."""
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('home')


# ======================= PRODUCT BROWSING VIEWS =======================

def home(request):
    """Home page with featured products."""
    featured_products = Product.objects.filter(availability=True)[:6]
    context = {'featured_products': featured_products}
    return render(request, 'store/home.html', context)


def product_list(request):
    """Display all products with search and filtering."""
    products = Product.objects.filter(availability=True).select_related('storeID')

    # Search by product name or description
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(productName__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by store
    store_id = request.GET.get('store', '')
    if store_id:
        products = products.filter(storeID=store_id)

    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Get all stores for filter dropdown
    stores = Store.objects.all()

    context = {
        'products': products,
        'stores': stores,
        'search_query': search_query,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, product_id):
    """Display product details, reviews, and promotions."""
    product = get_object_or_404(Product, productID=product_id)

    # Record click history if customer is logged in
    if 'customer_id' in request.session:
        customer_id = request.session['customer_id']
        try:
            customer = Customer.objects.get(customerID=customer_id)
            ClickHistory.objects.create(customerID=customer, productID=product)
        except Customer.DoesNotExist:
            pass

    # Get product media
    media = product.media.all()
    primary_image = media.filter(isPrimary=True).first()

    # Get reviews
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Get active promotions
    active_promo = None
    active_promotions = product.promotions.filter(status='active')
    for promo in active_promotions:
        if promo.is_active():
            active_promo = promo
            break

    # Check if product is in user's wishlist
    in_wishlist = False
    if 'customer_id' in request.session:
        try:
            customer = Customer.objects.get(customerID=request.session['customer_id'])
            in_wishlist = WishlistItem.objects.filter(
                customerID=customer, productID=product
            ).exists()
        except Customer.DoesNotExist:
            pass

    context = {
        'product': product,
        'media': media,
        'primary_image': primary_image,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
        'active_promo': active_promo,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'store/product_detail.html', context)


# ======================= CART VIEWS =======================

@require_POST
def add_to_cart(request, product_id):
    """Add product to cart."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in to add items to cart.")
        return redirect('customer_login')

    product = get_object_or_404(Product, productID=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        messages.error(request, "Invalid quantity.")
        return redirect('product_detail', product_id=product_id)

    if quantity > product.stockQuantity:
        messages.error(request, f"Only {product.stockQuantity} items available.")
        return redirect('product_detail', product_id=product_id)

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        cart_item, created = CartItem.objects.get_or_create(
            customerID=customer,
            productID=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, f"Added {product.productName} to cart.")
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect('product_detail', product_id=product_id)


def view_cart(request):
    """View shopping cart."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in to view your cart.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        cart_items = CartItem.objects.filter(customerID=customer).select_related('productID')
        
        total_price = Decimal('0.00')
        for item in cart_items:
            product = item.productID
            # Check for active promotion
            price = product.price
            for promo in product.promotions.filter(status='active'):
                if promo.is_active():
                    discount = promo.get_discount_amount(price)
                    price -= discount
                    break
            total_price += price * item.quantity

        context = {
            'cart_items': cart_items,
            'total_price': total_price,
        }
    except Customer.DoesNotExist:
        context = {'cart_items': [], 'total_price': 0}

    return render(request, 'store/cart.html', context)


@require_POST
def remove_from_cart(request, cart_item_id):
    """Remove item from cart."""
    if 'customer_id' not in request.session:
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        cart_item = get_object_or_404(CartItem, pk=cart_item_id, customerID=customer)
        product_name = cart_item.productID.productName
        cart_item.delete()
        messages.success(request, f"Removed {product_name} from cart.")
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect('view_cart')


@require_POST
def update_cart_item(request, cart_item_id):
    """Update quantity of item in cart."""
    if 'customer_id' not in request.session:
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        cart_item = get_object_or_404(CartItem, pk=cart_item_id, customerID=customer)
        quantity = int(request.POST.get('quantity', 1))

        if quantity < 1:
            cart_item.delete()
        elif quantity > cart_item.productID.stockQuantity:
            messages.error(request, f"Only {cart_item.productID.stockQuantity} items available.")
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated.")

    except Customer.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect('view_cart')


# ======================= ORDER VIEWS =======================

def checkout(request):
    """Checkout page."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in to checkout.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        cart_items = CartItem.objects.filter(customerID=customer).select_related('productID')

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('view_cart')

        # Calculate total
        total_amount = Decimal('0.00')
        order_data = []
        for item in cart_items:
            product = item.productID
            price = product.price
            # Apply promotion if available
            for promo in product.promotions.filter(status='active'):
                if promo.is_active():
                    discount = promo.get_discount_amount(price)
                    price -= discount
                    break
            subtotal = price * item.quantity
            total_amount += subtotal
            order_data.append({
                'cart_item': item,
                'final_price': price,
                'subtotal': subtotal
            })

        if request.method == 'POST':
            shipping_address = request.POST.get('shipping_address', '').strip()
            if not shipping_address:
                messages.error(request, "Shipping address is required.")
                return render(request, 'store/checkout.html', {
                    'cart_items': order_data,
                    'total_amount': total_amount,
                    'customer': customer,
                })

            # Create order
            order = Order.objects.create(
                customerID=customer,
                shippingAddress=shipping_address,
                totalAmount=total_amount
            )

            # Create order items
            for data in order_data:
                item = data['cart_item']
                OrderItem.objects.create(
                    orderID=order,
                    productID=item.productID,
                    quantity=item.quantity,
                    paidPrice=data['final_price']
                )
                # Create initial status
                order_item = OrderItem.objects.filter(orderID=order, productID=item.productID).last()
                OrderStatus.objects.create(
                    orderItemID=order_item,
                    status='Processing'
                )
                # Reduce stock
                item.productID.stockQuantity -= item.quantity
                item.productID.save()

            # Clear cart
            cart_items.delete()

            messages.success(request, f"Order created successfully! Order ID: {order.orderID}")
            return redirect('order_detail', order_id=order.orderID)

        context = {
            'cart_items': order_data,
            'total_amount': total_amount,
            'customer': customer,
        }
        return render(request, 'store/checkout.html', context)

    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')


def order_detail(request, order_id):
    """View order details."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        order = get_object_or_404(Order, orderID=order_id, customerID=customer)
        order_items = order.items.all().prefetch_related('statuses')

        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'store/order_detail.html', context)
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')


def order_history(request):
    """View customer's order history."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        orders = customer.orders.all().prefetch_related('items')

        context = {'orders': orders}
        return render(request, 'store/order_history.html', context)
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')


# ======================= REVIEW VIEWS =======================

@require_POST
def add_review(request, product_id):
    """Add a review to a product."""
    if 'customer_id' not in request.session:
        return JsonResponse({'error': 'Please log in'}, status=401)

    product = get_object_or_404(Product, productID=product_id)
    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()

        if rating < 1 or rating > 5:
            return JsonResponse({'error': 'Invalid rating'}, status=400)

        review, created = Review.objects.update_or_create(
            customerID=customer,
            productID=product,
            defaults={'rating': rating, 'comment': comment}
        )

        if created:
            message = "Review added successfully!"
        else:
            message = "Review updated successfully!"

        return JsonResponse({
            'success': True,
            'message': message,
            'review_id': review.reviewID
        })
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)


# ======================= WISHLIST VIEWS =======================

@require_POST
def toggle_wishlist(request, product_id):
    """Add or remove product from wishlist."""
    if 'customer_id' not in request.session:
        return JsonResponse({'error': 'Please log in'}, status=401)

    product = get_object_or_404(Product, productID=product_id)
    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])

        # Check for active promotion
        active_promo = None
        discount_rate = Decimal('0.00')
        for promo in product.promotions.filter(status='active'):
            if promo.is_active():
                active_promo = promo
                discount_rate = promo.discountRate
                break

        wishlist_item, created = WishlistItem.objects.get_or_create(
            customerID=customer,
            productID=product,
            defaults={
                'originalPrice': product.price,
                'discountRate': discount_rate,
                'priceAtAddedTime': product.price - (product.price * discount_rate / 100)
            }
        )

        if created:
            return JsonResponse({'success': True, 'message': 'Added to wishlist', 'action': 'added'})
        else:
            wishlist_item.delete()
            return JsonResponse({'success': True, 'message': 'Removed from wishlist', 'action': 'removed'})

    except Customer.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)


def view_wishlist(request):
    """View customer's wishlist."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in to view your wishlist.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        wishlist_items = customer.wishlist_items.all().select_related('productID')

        context = {'wishlist_items': wishlist_items}
        return render(request, 'store/wishlist.html', context)
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')


# ======================= VENDOR DASHBOARD VIEWS =======================

def vendor_dashboard(request):
    """Vendor dashboard - main page."""
    if 'vendor_id' not in request.session:
        messages.error(request, "Please log in as a vendor.")
        return redirect('vendor_login')

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        store = vendor.store
        products = store.products.all()
        total_sales = Order.objects.filter(items__productID__storeID=store).aggregate(
            total=Decimal('0.00')
        )['total'] or Decimal('0.00')

        context = {
            'vendor': vendor,
            'store': store,
            'products': products,
            'total_products': products.count(),
            'total_sales': total_sales,
        }
        return render(request, 'store/vendor_dashboard.html', context)
    except Vendor.DoesNotExist:
        messages.error(request, "Vendor not found.")
        return redirect('vendor_login')


@require_POST
def add_product(request):
    """Add a new vinyl product (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        store = vendor.store

        product_name = request.POST.get('productName', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', 0)
        stock = request.POST.get('stockQuantity', 0)

        if not product_name or not price or not stock:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        product = Product.objects.create(
            storeID=store,
            productName=product_name,
            description=description,
            price=Decimal(price),
            stockQuantity=int(stock),
            availability=True
        )

        return JsonResponse({
            'success': True,
            'message': 'Product added successfully',
            'product_id': product.productID
        })
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def edit_product(request, product_id):
    """Edit product details (vendor only)."""
    if 'vendor_id' not in request.session:
        messages.error(request, "Please log in as a vendor.")
        return redirect('vendor_login')

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        product = get_object_or_404(Product, productID=product_id, storeID=vendor.store)

        if request.method == 'POST':
            product.productName = request.POST.get('productName', product.productName)
            product.description = request.POST.get('description', product.description)
            product.price = Decimal(request.POST.get('price', product.price))
            product.stockQuantity = int(request.POST.get('stockQuantity', product.stockQuantity))
            product.save()

            messages.success(request, "Product updated successfully!")
            return redirect('vendor_dashboard')

        context = {'product': product}
        return render(request, 'store/edit_product.html', context)
    except Vendor.DoesNotExist:
        messages.error(request, "Vendor not found.")
        return redirect('vendor_login')


@require_POST
def upload_product_image(request, product_id):
    """Upload image for a product (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        product = get_object_or_404(Product, productID=product_id, storeID=vendor.store)

        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)

        is_primary = request.POST.get('is_primary', 'false').lower() == 'true'

        # If marking as primary, unset others
        if is_primary:
            product.media.filter(isPrimary=True).update(isPrimary=False)

        media = ProductMedia.objects.create(
            productID=product,
            mediaURL=request.FILES['image'],
            isPrimary=is_primary,
            sortedOrder=product.media.count()
        )

        return JsonResponse({
            'success': True,
            'message': 'Image uploaded successfully',
            'media_id': media.mediaID
        })
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

