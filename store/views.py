from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Avg, Sum, Count
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile
from decimal import Decimal
from io import BytesIO
from PIL import Image
import json

from .models import (
    Customer, Vendor, Store, Product, ProductMedia, CartItem, Order, OrderItem,
    OrderStatus, Review, WishlistItem, Promotion, ClickHistory, StoreMedia, RefundRequest,
    CancelledItem, Notification, SearchQuery
)


def _expire_past_promotions():
    """Auto-expire promotions whose endDate has passed but status is still 'active'."""
    Promotion.objects.filter(
        status='active',
        endDate__lt=timezone.now()
    ).update(status='expired')


# ======================= HELPERS =======================

REVIEW_PHOTO_SIZE = (800, 800)  # max width × height; aspect ratio preserved

def _resize_review_photo(upload):
    """Resize an uploaded review photo to fit within REVIEW_PHOTO_SIZE, return InMemoryUploadedFile."""
    img = Image.open(upload)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    elif img.mode == 'RGBA':
        bg = Image.new('RGB', img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    img.thumbnail(REVIEW_PHOTO_SIZE, Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=85, optimize=True)
    buf.seek(0)
    return InMemoryUploadedFile(
        buf, 'ImageField',
        upload.name.rsplit('.', 1)[0] + '.jpg',
        'image/jpeg', buf.getbuffer().nbytes, None
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
    _expire_past_promotions()
    all_products = list(
        Product.objects.filter(availability=True)
        .select_related('storeID')
        .prefetch_related('promotions')
        .annotate(avg_rating=Avg('reviews__rating'))
    )

    # Annotate each product with discount info
    for product in all_products:
        promo = product.promotions.filter(status='active').first()
        if promo and promo.is_active():
            product.has_discount = True
            product.discount_percent = int(promo.discountRate)
            product.discounted_price = product.price - promo.get_discount_amount(product.price)
        else:
            product.has_discount = False
            product.discount_percent = 0
            product.discounted_price = product.price

    on_sale = [p for p in all_products if p.has_discount][:10]
    featured_products = [p for p in all_products if not p.has_discount][:6]

    context = {
        'featured_products': featured_products,
        'on_sale': on_sale,
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """Display all products with search and filtering."""
    _expire_past_promotions()
    products = Product.objects.filter(availability=True).select_related('storeID').prefetch_related('promotions').annotate(
        avg_rating=Avg('reviews__rating')
    )

    # Search by product name or description
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(productName__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        # Log search query for analytics
        customer = None
        if 'customer_id' in request.session:
            try:
                customer = Customer.objects.get(customerID=request.session['customer_id'])
            except Customer.DoesNotExist:
                pass
        SearchQuery.objects.create(
            customerID=customer,
            query=search_query,
            resultCount=products.count()
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

    # Evaluate queryset then annotate discount info (must be after all filters)
    products = list(products)
    for product in products:
        promo = product.promotions.filter(status='active').first()
        if promo and promo.is_active():
            discount_amount = promo.get_discount_amount(product.price)
            product.discounted_price = product.price - discount_amount
            product.discount_percent = int(promo.discountRate)
            product.has_discount = True
        else:
            product.discounted_price = product.price
            product.discount_percent = 0
            product.has_discount = False

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 9)  # 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all stores for filter dropdown
    stores = Store.objects.all()

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'stores': stores,
        'search_query': search_query,
    }
    return render(request, 'store/product_list.html', context)


def shop_detail(request, store_id):
    """Public shop page — store info, gallery, and searchable product listing."""
    _expire_past_promotions()
    store = get_object_or_404(Store, storeID=store_id)
    search_query = request.GET.get('search', '').strip()

    products = Product.objects.filter(
        storeID=store, availability=True
    ).prefetch_related('promotions', 'media').annotate(
        avg_rating=Avg('reviews__rating')
    )

    if search_query:
        products = products.filter(
            Q(productName__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        # Log search query for analytics
        customer = None
        if 'customer_id' in request.session:
            try:
                customer = Customer.objects.get(customerID=request.session['customer_id'])
            except Customer.DoesNotExist:
                pass
        SearchQuery.objects.create(
            customerID=customer,
            query=search_query,
            resultCount=products.count()
        )

    for product in products:
        promo = product.promotions.filter(status='active').first()
        if promo and promo.is_active():
            product.discounted_price = product.price - promo.get_discount_amount(product.price)
            product.has_discount = True
            product.active_promo = promo
        else:
            product.discounted_price = product.price
            product.has_discount = False
            product.active_promo = None

    shop_photos = store.shop_photos.all()

    context = {
        'store': store,
        'products': products,
        'shop_photos': shop_photos,
        'search_query': search_query,
        'product_count': products.count(),
    }
    return render(request, 'store/shop.html', context)


def product_detail(request, product_id):
    """Display product details, reviews, and promotions."""
    _expire_past_promotions()
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
    # Try to get primary image, fall back to first image if no primary is marked
    primary_image = media.filter(isPrimary=True).first()
    if not primary_image and media.exists():
        primary_image = media.first()

    # Get reviews
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Get active promotions
    active_promo = None
    discounted_price = None
    active_promotions = product.promotions.filter(status='active')
    for promo in active_promotions:
        if promo.is_active():
            active_promo = promo
            # Calculate the discounted price
            discount_amount = promo.get_discount_amount(product.price)
            discounted_price = product.price - discount_amount
            break

    # Check if product is in user's wishlist and if customer has purchased the product
    in_wishlist = False
    has_purchased = False
    if 'customer_id' in request.session:
        try:
            customer = Customer.objects.get(customerID=request.session['customer_id'])
            in_wishlist = WishlistItem.objects.filter(
                customerID=customer, productID=product
            ).exists()
            # Check if customer has purchased this product
            has_purchased = OrderItem.objects.filter(
                orderID__customerID=customer,
                productID=product
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
        'discounted_price': discounted_price,
        'in_wishlist': in_wishlist,
        'has_purchased': has_purchased,
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
        cart_items = CartItem.objects.filter(customerID=customer).select_related('productID').prefetch_related('productID__promotions')
        _expire_past_promotions()
        
        total_price = Decimal('0.00')
        for item in cart_items:
            product = item.productID
            # Check for active promotion
            price = product.price
            has_promo = False
            for promo in product.promotions.filter(status='active'):
                if promo.is_active():
                    discount = promo.get_discount_amount(price)
                    price -= discount
                    has_promo = True
                    break
            
            # Add computed subtotal properties
            item.effective_price = price
            item.subtotal = product.price * item.quantity
            item.subtotal_with_promo = price * item.quantity
            
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
    """Checkout page — only selected cart items are checked out."""
    _expire_past_promotions()
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in to checkout.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])

        # Get selected item IDs from query string (GET) or form (POST)
        selected_ids = request.GET.getlist('items') or request.POST.getlist('items')
        selected_ids = [int(i) for i in selected_ids if i.isdigit()]

        if not selected_ids:
            messages.error(request, "No items selected for checkout.")
            return redirect('view_cart')

        cart_items = CartItem.objects.filter(
            customerID=customer, pk__in=selected_ids
        ).select_related('productID').prefetch_related('productID__promotions')

        if not cart_items.exists():
            messages.error(request, "Selected items not found in your cart.")
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
                    'selected_ids': selected_ids,
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

            # Only delete the checked-out items from cart; unselected items remain
            cart_items.delete()

            # Notify vendors about the new order
            vendor_ids_seen = set()
            for data in order_data:
                vid = data['cart_item'].productID.storeID.vendorID_id
                if vid not in vendor_ids_seen:
                    vendor_ids_seen.add(vid)
                    Notification.objects.create(
                        vendorID_id=vid,
                        notificationType='new_order',
                        title='New Order Received',
                        message=f'Order #{order.orderID} has been placed by {customer.firstName} {customer.lastName}.',
                        link=f'/vendor/orders/'
                    )

            messages.success(request, f"Order created successfully! Order ID: {order.orderID}")
            return redirect('order_detail', order_id=order.orderID)

        context = {
            'cart_items': order_data,
            'total_amount': total_amount,
            'customer': customer,
            'selected_ids': selected_ids,
        }
        return render(request, 'store/checkout.html', context)

    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')


def _get_order_aggregate_status(order):
    """Compute an aggregate display status for an order with multiple items.
    Priority (worst-case shown): Processing > Holding > Shipping > Completed.
    If ANY item is Cancelled and others are not, show the non-cancelled worst status.
    If ALL items are Cancelled, show Cancelled.
    """
    priority = {'Processing': 0, 'Holding': 1, 'Shipping': 2, 'Completed': 3, 'Cancelled': 4}
    worst = None
    all_cancelled = True
    for item in order.items.all():
        latest = item.statuses.order_by('-updatedDate').first()
        if not latest:
            continue
        s = latest.status
        if s != 'Cancelled':
            all_cancelled = False
        if s == 'Cancelled':
            continue  # skip cancelled when computing worst non-cancelled
        if worst is None or priority.get(s, 99) < priority.get(worst, 99):
            worst = s
    if all_cancelled:
        return 'Cancelled'
    return worst or 'Processing'


def order_detail(request, order_id):
    """View order details."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        order = get_object_or_404(Order, orderID=order_id, customerID=customer)
        order_items = order.items.all().prefetch_related('statuses', 'refund_requests')
        
        # Add subtotal and cancellable flag to each order item
        for item in order_items:
            item.subtotal = item.paidPrice * item.quantity
            latest_status = item.statuses.order_by('-updatedDate').first()
            item.latest_status_obj = latest_status
            # Item can be cancelled if status is Processing or Holding
            item.can_cancel = latest_status and latest_status.status in ['Processing', 'Holding']
            # Item can request refund if Shipping or Completed
            item.can_request_refund = latest_status and latest_status.status in ['Shipping', 'Completed']
            # Check for existing pending refund
            item.has_pending_refund = item.refund_requests.filter(status='pending').exists()
            # Full status history for timeline
            item.status_history = item.statuses.order_by('updatedDate')

        # Aggregate order-level status
        order.aggregate_status = _get_order_aggregate_status(order)

        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'store/order_detail.html', context)
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')


def order_history(request):
    """View customer's order history with status filtering."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        orders = list(
            customer.orders.all()
            .prefetch_related('items__statuses')
            .order_by('-orderDate')
        )

        # Compute aggregate status for each order
        for order in orders:
            order.aggregate_status = _get_order_aggregate_status(order)

        # Filter by status if provided
        status_filter = request.GET.get('status', '').strip()
        if status_filter:
            orders = [o for o in orders if o.aggregate_status == status_filter]
        
        # Get available status choices for the filter dropdown
        from store.models import OrderStatus
        status_choices = OrderStatus.STATUS_CHOICES

        context = {
            'orders': orders,
            'status_choices': status_choices,
            'current_status': status_filter
        }
        return render(request, 'store/order_history.html', context)
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')


@require_POST
def cancel_order_item(request, order_item_id):
    """Cancel an order item (customer only, before shipping)."""
    if 'customer_id' not in request.session:
        return JsonResponse({'error': 'Please log in'}, status=401)

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        order_item = get_object_or_404(
            OrderItem,
            orderItemID=order_item_id,
            orderID__customerID=customer
        )
        
        # Check current status
        latest_status = order_item.statuses.last()
        if not latest_status:
            return JsonResponse({'error': 'Order item has no status'}, status=400)
        
        # Can only cancel if status is Processing or Holding
        if latest_status.status not in ['Processing', 'Holding']:
            return JsonResponse({
                'error': f'Cannot cancel item with status: {latest_status.status}'
            }, status=400)
        
        # Create new Cancelled status
        cancelled_status = OrderStatus.objects.create(
            orderItemID=order_item,
            status='Cancelled'
        )
        
        # Create cancellation record
        CancelledItem.objects.create(
            statusID=cancelled_status,
            cancelledReason='customer_request'
        )
        
        # Restore product stock
        product = order_item.productID
        product.stockQuantity += order_item.quantity
        product.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Order item cancelled successfully'
        })
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ======================= REVIEW VIEWS =======================


@require_POST
def request_refund(request, order_item_id):
    """Submit a refund request for a shipped/completed order item."""
    if 'customer_id' not in request.session:
        return JsonResponse({'error': 'Please log in'}, status=401)

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        order_item = get_object_or_404(
            OrderItem,
            orderItemID=order_item_id,
            orderID__customerID=customer
        )

        latest_status = order_item.statuses.last()
        if not latest_status or latest_status.status not in ['Shipping', 'Completed']:
            return JsonResponse({'error': 'Refund can only be requested for shipped or completed items'}, status=400)

        if order_item.refund_requests.filter(status='pending').exists():
            return JsonResponse({'error': 'A refund request is already pending for this item'}, status=400)

        reason = request.POST.get('reason', '').strip()
        if not reason:
            return JsonResponse({'error': 'Please provide a reason'}, status=400)

        RefundRequest.objects.create(orderItemID=order_item, reason=reason)

        # Notify the vendor about the refund request
        vendor = order_item.productID.storeID.vendorID
        Notification.objects.create(
            vendorID=vendor,
            notificationType='refund_request',
            title='Refund Request Received',
            message=f'{customer.firstName} {customer.lastName} requested a refund for "{order_item.productID.productName}".',
            link='/vendor/orders/'
        )

        return JsonResponse({'success': True, 'message': 'Refund request submitted successfully'})
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def add_review(request, product_id):
    """Add a review to a product."""
    if 'customer_id' not in request.session:
        return JsonResponse({'error': 'Please log in'}, status=401)

    product = get_object_or_404(Product, productID=product_id)
    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        
        # Check if customer has purchased this product
        has_purchased = OrderItem.objects.filter(
            orderID__customerID=customer,
            productID=product
        ).exists()
        
        if not has_purchased:
            return JsonResponse({'error': 'You can only review products you have purchased'}, status=403)
        
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()

        if rating < 1 or rating > 5:
            return JsonResponse({'error': 'Invalid rating'}, status=400)

        photo = request.FILES.get('photo')
        kwargs = {'rating': rating, 'comment': comment}
        if photo:
            kwargs['photo'] = _resize_review_photo(photo)

        review = Review.objects.create(
            customerID=customer,
            productID=product,
            **kwargs
        )

        return JsonResponse({
            'success': True,
            'message': 'Review posted successfully!',
            'review_id': review.reviewID
        })
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)


@require_POST
def delete_review(request, review_id):
    """Delete the logged-in customer's own review."""
    if 'customer_id' not in request.session:
        return JsonResponse({'error': 'Please log in'}, status=401)
    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        review = get_object_or_404(Review, reviewID=review_id, customerID=customer)
        # Remove stored photo file from disk
        if review.photo:
            review.photo.delete(save=False)
        review.delete()
        return JsonResponse({'success': True})
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=400)


# ======================= WISHLIST VIEWS =======================

@require_POST
def toggle_wishlist(request, product_id):
    """Add or remove product from wishlist."""
    if 'customer_id' not in request.session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Please log in'}, status=401)
        messages.error(request, "Please log in to manage your wishlist.")
        return redirect('customer_login')

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
            message = 'Added to wishlist'
            action = 'added'
        else:
            wishlist_item.delete()
            message = 'Removed from wishlist'
            action = 'removed'

        # Return JSON if AJAX request, otherwise redirect
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': message, 'action': action})
        else:
            messages.success(request, message)
            return redirect('view_wishlist')

    except Customer.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'User not found'}, status=400)
        messages.error(request, "User not found.")
        return redirect('view_wishlist')


def view_wishlist(request):
    """View customer's wishlist."""
    _expire_past_promotions()
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in to view your wishlist.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        wishlist_items = list(
            customer.wishlist_items.all()
            .select_related('productID')
            .prefetch_related('productID__promotions')
        )

        now = timezone.now()
        for item in wishlist_items:
            active_promo = next(
                (p for p in item.productID.promotions.all() if p.is_active()),
                None
            )
            item.active_promo = active_promo
            item.has_active_promo = active_promo is not None
            # Compute live discounted price from current product price & active promo
            if active_promo:
                discount_amount = active_promo.get_discount_amount(item.productID.price)
                item.live_discounted_price = item.productID.price - discount_amount
            else:
                item.live_discounted_price = item.productID.price
            # Sort discount: use live rate if active promo, else 0 (no discount)
            item.sort_discount = float(active_promo.discountRate) if active_promo else 0

        wishlist_items.sort(key=lambda x: (
            x.sort_discount <= 0,
            -x.sort_discount
        ))

        context = {'wishlist_items': wishlist_items}
        return render(request, 'store/wishlist.html', context)
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')


def view_click_history(request):
    """View customer's click history (viewed products)."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in to view your click history.")
        return redirect('customer_login')

    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
        # Get click history ordered by most recent first, deduplicated per product
        all_history = customer.click_history.all().select_related('productID').order_by('-viewedDate')
        seen = set()
        click_history = []
        for entry in all_history:
            if entry.productID_id not in seen:
                seen.add(entry.productID_id)
                click_history.append(entry)

        context = {'click_history': click_history}
        return render(request, 'store/click_history.html', context)
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')


def customer_profile(request):
    """View and edit customer profile information."""
    if 'customer_id' not in request.session:
        messages.error(request, "Please log in to view your profile.")
        return redirect('customer_login')
    try:
        customer = Customer.objects.get(customerID=request.session['customer_id'])
    except Customer.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('customer_login')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not first_name or not last_name:
            messages.error(request, 'First and last name are required.')
            return redirect('customer_profile')

        if new_password:
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return redirect('customer_profile')
            if len(new_password) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
                return redirect('customer_profile')
            customer.set_password(new_password)

        customer.firstName = first_name
        customer.lastName = last_name
        customer.phoneNumber = phone
        customer.shippingAddress = shipping_address
        customer.save()

        request.session['customer_name'] = f"{first_name} {last_name}"
        messages.success(request, 'Profile updated successfully!')
        return redirect('customer_profile')

    return render(request, 'store/customer_profile.html', {'customer': customer})


# ======================= VENDOR DASHBOARD VIEWS =======================

def vendor_dashboard(request):
    """Vendor dashboard - main page."""
    if 'vendor_id' not in request.session:
        messages.error(request, "Please log in as a vendor.")
        return redirect('vendor_login')

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        store = vendor.store
        products = store.products.all().annotate(
            wishlist_count=Count('wishlistitem')
        )

        # Vendor product search
        vendor_search = request.GET.get('vendor_search', '').strip()
        if vendor_search:
            import re
            id_match = re.match(r'^ID:(\d+)$', vendor_search, re.IGNORECASE)
            if id_match:
                products = products.filter(productID=int(id_match.group(1)))
            else:
                products = products.filter(
                    Q(productName__icontains=vendor_search) |
                    Q(description__icontains=vendor_search)
                )
        
        # Calculate total sales from orders (excluding cancelled items)
        from django.db.models import F
        order_items = OrderItem.objects.filter(
            productID__storeID=store
        ).prefetch_related('statuses')
        
        total_sales = Decimal('0.00')
        for item in order_items:
            latest_status = item.statuses.last()
            # Only count non-cancelled items
            if latest_status and latest_status.status != 'Cancelled':
                total_sales += item.paidPrice * item.quantity

        # Product insights: most wishlisted products
        top_wishlisted = store.products.annotate(
            wl_count=Count('wishlistitem')
        ).filter(wl_count__gt=0).order_by('-wl_count')[:5]

        # Product insights: most viewed products (last 30 days)
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        top_viewed = store.products.filter(
            clickhistory__viewedDate__gte=thirty_days_ago
        ).annotate(
            view_count=Count('clickhistory')
        ).order_by('-view_count')[:5]

        # Search analytics: top search terms that returned this store's products (last 30 days)
        store_product_names = list(store.products.values_list('productName', flat=True))
        recent_searches = SearchQuery.objects.filter(
            searchedAt__gte=thirty_days_ago
        ).values('query').annotate(
            search_count=Count('searchID')
        ).order_by('-search_count')[:10]

        context = {
            'vendor': vendor,
            'store': store,
            'products': products,
            'total_products': store.products.count(),
            'total_sales': total_sales,
            'shop_photos': store.shop_photos.all(),
            'vendor_search': vendor_search,
            'top_wishlisted': top_wishlisted,
            'top_viewed': top_viewed,
            'recent_searches': recent_searches,
        }
        return render(request, 'store/vendor_dashboard.html', context)
    except Vendor.DoesNotExist:
        messages.error(request, "Vendor not found.")
        return redirect('vendor_login')


@require_POST
def upload_vendor_profile(request):
    """Upload or replace the vendor's profile picture."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)
    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        image = request.FILES.get('profile_image')
        if not image:
            return JsonResponse({'error': 'No image provided'}, status=400)
        if vendor.profileImage:
            try:
                import os
                if os.path.isfile(vendor.profileImage.path):
                    os.remove(vendor.profileImage.path)
            except Exception:
                pass
        vendor.profileImage = image
        vendor.save()
        return JsonResponse({'success': True, 'url': vendor.profileImage.url})
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=404)


@require_POST
def upload_store_photo(request):
    """Upload a shop gallery photo (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)
    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        store = vendor.store
        image = request.FILES.get('photo')
        caption = request.POST.get('caption', '').strip()
        if not image:
            return JsonResponse({'error': 'No image provided'}, status=400)
        photo = StoreMedia.objects.create(storeID=store, image=image, caption=caption)
        return JsonResponse({'success': True, 'id': photo.storeMediaID, 'url': photo.image.url, 'caption': photo.caption})
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=404)


@require_POST
def delete_store_photo(request, photo_id):
    """Delete a shop gallery photo (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)
    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        photo = get_object_or_404(StoreMedia, storeMediaID=photo_id, storeID=vendor.store)
        try:
            import os
            if os.path.isfile(photo.image.path):
                os.remove(photo.image.path)
        except Exception:
            pass
        photo.delete()
        return JsonResponse({'success': True})
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=404)


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
    _expire_past_promotions()
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

        # Get existing promotions
        promotions = product.promotions.all().order_by('-createdTime')
        # Get product images
        media = product.media.all().order_by('sortedOrder')
        # Wishlist count for this product
        wishlist_count = WishlistItem.objects.filter(productID=product).count()
        
        context = {
            'product': product,
            'promotions': promotions,
            'media': media,
            'wishlist_count': wishlist_count,
        }
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


@require_POST
def set_primary_image(request, media_id):
    """Set an existing image as primary (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        media = get_object_or_404(
            ProductMedia,
            mediaID=media_id,
            productID__storeID=vendor.store
        )
        
        # Unset all other primary images for this product
        media.productID.media.filter(isPrimary=True).update(isPrimary=False)
        
        # Set this image as primary
        media.isPrimary = True
        media.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Primary image updated successfully'
        })
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
def delete_product_image(request, media_id):
    """Delete a product image (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        media = get_object_or_404(
            ProductMedia,
            mediaID=media_id,
            productID__storeID=vendor.store
        )
        
        # Delete the image file and database record
        media.mediaURL.delete()
        media.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Image deleted successfully'
        })
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
def toggle_product_availability(request, product_id):
    """Toggle product availability (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        product = get_object_or_404(Product, productID=product_id, storeID=vendor.store)
        
        # Toggle availability
        product.availability = not product.availability
        product.save()
        
        status_text = 'enabled' if product.availability else 'disabled'
        
        return JsonResponse({
            'success': True,
            'message': f'Product {status_text} successfully',
            'availability': product.availability
        })
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ======================= PROMOTION MANAGEMENT =======================

@require_POST
def add_promotion(request, product_id):
    """Add a promotion/discount to a product (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        product = get_object_or_404(Product, productID=product_id, storeID=vendor.store)
        
        discount_rate = request.POST.get('discount_rate', '').strip()
        start_date = request.POST.get('start_date', '').strip()
        end_date = request.POST.get('end_date', '').strip()
        
        if not discount_rate or not start_date or not end_date:
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        discount_rate = Decimal(discount_rate)
        if discount_rate <= 0 or discount_rate > 100:
            return JsonResponse({'error': 'Discount rate must be between 0 and 100'}, status=400)
        
        # Parse datetime strings and make them timezone-aware
        from datetime import datetime
        from django.utils import timezone as tz
        
        # Parse the datetime string (comes from datetime-local input as naive datetime)
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Make timezone-aware if naive (use default timezone from settings)
        if start_dt.tzinfo is None:
            start_dt = tz.make_aware(start_dt)
        if end_dt.tzinfo is None:
            end_dt = tz.make_aware(end_dt)
        
        if end_dt <= start_dt:
            return JsonResponse({'error': 'End date must be after start date'}, status=400)
        
        promotion = Promotion.objects.create(
            productID=product,
            discountRate=discount_rate,
            startDate=start_dt,
            endDate=end_dt,
            status='active'
        )

        # If promotion is already active, notify wishlist customers
        if promotion.is_active():
            wishlist_customer_ids = WishlistItem.objects.filter(
                productID=product
            ).values_list('customerID_id', flat=True)
            notifications = [
                Notification(
                    customerID_id=cid,
                    notificationType='wishlist_promo',
                    title='Wishlist Item On Sale!',
                    message=f'"{product.productName}" is now {discount_rate}% off!',
                    link=f'/products/{product.productID}/'
                )
                for cid in wishlist_customer_ids
            ]
            if notifications:
                Notification.objects.bulk_create(notifications)

        return JsonResponse({
            'success': True,
            'message': 'Promotion added successfully',
            'promotion_id': promotion.promotionID
        })
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
def delete_promotion(request, promotion_id):
    """Delete a promotion (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        promotion = get_object_or_404(
            Promotion,
            promotionID=promotion_id,
            productID__storeID=vendor.store
        )
        
        promotion.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Promotion deleted successfully'
        })
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
def toggle_promotion_status(request, promotion_id):
    """Toggle promotion active/inactive status (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        promotion = get_object_or_404(
            Promotion,
            promotionID=promotion_id,
            productID__storeID=vendor.store
        )
        
        # Toggle between active and inactive
        promotion.status = 'inactive' if promotion.status == 'active' else 'active'
        promotion.save()

        # If promotion just became active, notify customers who have this product wishlisted
        if promotion.status == 'active' and promotion.is_active():
            product = promotion.productID
            wishlist_customer_ids = WishlistItem.objects.filter(
                productID=product
            ).values_list('customerID_id', flat=True)
            notifications = [
                Notification(
                    customerID_id=cid,
                    notificationType='wishlist_promo',
                    title='Wishlist Item On Sale!',
                    message=f'"{product.productName}" is now {promotion.discountRate}% off!',
                    link=f'/products/{product.productID}/'
                )
                for cid in wishlist_customer_ids
            ]
            if notifications:
                Notification.objects.bulk_create(notifications)

        return JsonResponse({
            'success': True,
            'message': f'Promotion {promotion.status}',
            'status': promotion.status
        })
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
def respond_refund(request, refund_id):
    """Vendor approves or rejects a customer refund request."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        refund = get_object_or_404(RefundRequest, refundRequestID=refund_id,
                                   orderItemID__productID__storeID=vendor.store)
        action = request.POST.get('action')
        if action not in ['approve', 'reject']:
            return JsonResponse({'error': 'Invalid action'}, status=400)

        vendor_note = request.POST.get('vendor_note', '').strip()
        refund.status = 'approved' if action == 'approve' else 'rejected'
        refund.vendorNote = vendor_note
        refund.responseDate = timezone.now()
        refund.save()

        if action == 'approve':
            order_item = refund.orderItemID
            OrderStatus.objects.create(orderItemID=order_item, status='Cancelled')
            product = order_item.productID
            product.stockQuantity += order_item.quantity
            product.save()
            message = 'Refund approved and item cancelled'
        else:
            message = 'Refund request rejected'

        # Notify the customer about the refund decision
        customer = refund.orderItemID.orderID.customerID
        status_word = 'approved' if action == 'approve' else 'rejected'
        note_text = f' Note: "{vendor_note}"' if vendor_note else ''
        Notification.objects.create(
            customerID=customer,
            notificationType='refund_response',
            title=f'Refund {status_word.title()}',
            message=f'Your refund request for "{refund.orderItemID.productID.productName}" has been {status_word}.{note_text}',
            link=f'/orders/{refund.orderItemID.orderID.orderID}/'
        )

        return JsonResponse({'success': True, 'message': message})
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ======================= VENDOR ORDER MANAGEMENT =======================

def vendor_orders(request):
    """View all orders containing vendor's products."""
    if 'vendor_id' not in request.session:
        messages.error(request, "Please log in as a vendor.")
        return redirect('vendor_login')

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        store = vendor.store
        
        # Get all order items for products in this vendor's store
        order_items = OrderItem.objects.filter(
            productID__storeID=store
        ).select_related(
            'orderID', 'orderID__customerID', 'productID'
        ).prefetch_related('statuses').order_by('-orderID__orderDate')
        
        # Group order items by order for better display
        orders_dict = {}
        for item in order_items:
            order = item.orderID
            if order.orderID not in orders_dict:
                orders_dict[order.orderID] = {
                    'order': order,
                    'items': []
                }
            # Add latest status to item
            item.latest_status = item.statuses.last()
            # Vendors cannot update status if item is cancelled by customer
            item.can_update_status = item.latest_status.status != 'Cancelled' if item.latest_status else True
            # Computed subtotal for display
            item.subtotal = item.paidPrice * item.quantity
            # Pending refund request from customer
            item.pending_refund = item.refund_requests.filter(status='pending').first()
            orders_dict[order.orderID]['items'].append(item)
        
        # Convert to list and sort by order date
        orders_data = sorted(orders_dict.values(), 
                           key=lambda x: x['order'].orderDate, 
                           reverse=True)
        
        context = {
            'vendor': vendor,
            'store': store,
            'orders_data': orders_data,
        }
        return render(request, 'store/vendor_orders.html', context)
    except Vendor.DoesNotExist:
        messages.error(request, "Vendor not found.")
        return redirect('vendor_login')


@require_POST
def update_order_status(request, order_item_id):
    """Update the status of an order item (vendor only)."""
    if 'vendor_id' not in request.session:
        return JsonResponse({'error': 'Please log in as vendor'}, status=401)

    try:
        vendor = Vendor.objects.get(vendorID=request.session['vendor_id'])
        store = vendor.store
        
        # Get the order item and verify it belongs to this vendor's store
        order_item = get_object_or_404(
            OrderItem, 
            orderItemID=order_item_id,
            productID__storeID=store
        )
        
        new_status = request.POST.get('status', '').strip()
        
        # Validate status
        valid_statuses = [choice[0] for choice in OrderStatus.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        # Create new status record
        status_record = OrderStatus.objects.create(
            orderItemID=order_item,
            status=new_status
        )

        # Notify the customer about the status change
        customer = order_item.orderID.customerID
        Notification.objects.create(
            customerID=customer,
            notificationType='order_status',
            title=f'Order Status: {new_status}',
            message=f'Your order item "{order_item.productID.productName}" status changed to {new_status}.',
            link=f'/orders/{order_item.orderID.orderID}/'
        )

        return JsonResponse({
            'success': True,
            'message': f'Status updated to {new_status}',
            'status': new_status,
            'updated_date': status_record.updatedDate.strftime('%b %d, %Y %H:%M')
        })
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ======================= NOTIFICATION VIEWS =======================

def notifications_page(request):
    """Display notification list for the logged-in customer or vendor."""
    if request.session.get('user_type') == 'customer' and 'customer_id' in request.session:
        notifs = Notification.objects.filter(customerID_id=request.session['customer_id'])
    elif request.session.get('user_type') == 'vendor' and 'vendor_id' in request.session:
        notifs = Notification.objects.filter(vendorID_id=request.session['vendor_id'])
    else:
        messages.error(request, 'Please log in to view notifications.')
        return redirect('home')

    return render(request, 'store/notifications.html', {'notifications': notifs})


def notifications_json(request):
    """Return recent notifications as JSON for the dropdown."""
    from django.utils.timesince import timesince
    user_type = request.session.get('user_type')
    if user_type == 'customer' and request.session.get('customer_id'):
        qs = Notification.objects.filter(customerID_id=request.session['customer_id'])
    elif user_type == 'vendor' and request.session.get('vendor_id'):
        qs = Notification.objects.filter(vendorID_id=request.session['vendor_id'])
    else:
        return JsonResponse({'notifications': [], 'unread': 0})

    notifs = qs.order_by('-createdTime')[:20]
    data = []
    for n in notifs:
        data.append({
            'id': n.notificationID,
            'type': n.notificationType,
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'is_read': n.isRead,
            'time_ago': timesince(n.createdTime) + ' ago',
        })
    unread = qs.filter(isRead=False).count()
    return JsonResponse({'notifications': data, 'unread': unread})


@require_POST
def mark_notification_read(request, notification_id):
    """Mark a single notification as read (AJAX)."""
    notif = get_object_or_404(Notification, notificationID=notification_id)
    # Verify ownership
    cid = request.session.get('customer_id')
    vid = request.session.get('vendor_id')
    if not ((notif.customerID_id and notif.customerID_id == cid) or
            (notif.vendorID_id and notif.vendorID_id == vid)):
        return JsonResponse({'error': 'Not authorized'}, status=403)

    notif.isRead = True
    notif.save()
    return JsonResponse({'success': True})


@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read for the logged-in user."""
    if request.session.get('user_type') == 'customer' and 'customer_id' in request.session:
        Notification.objects.filter(customerID_id=request.session['customer_id'], isRead=False).update(isRead=True)
    elif request.session.get('user_type') == 'vendor' and 'vendor_id' in request.session:
        Notification.objects.filter(vendorID_id=request.session['vendor_id'], isRead=False).update(isRead=True)
    else:
        return JsonResponse({'error': 'Not logged in'}, status=401)
    return JsonResponse({'success': True})

