from .models import Customer, CartItem, Notification


def cart_count(request):
    """Add cart_item_count to every template context for logged-in customers."""
    count = 0
    if request.session.get('user_type') == 'customer' and request.session.get('customer_id'):
        try:
            count = CartItem.objects.filter(
                customerID_id=request.session['customer_id']
            ).count()
        except Exception:
            pass
    return {'cart_item_count': count}


def unread_notification_count(request):
    """Add unread_notif_count to every template context."""
    count = 0
    user_type = request.session.get('user_type')
    try:
        if user_type == 'customer' and request.session.get('customer_id'):
            count = Notification.objects.filter(
                customerID_id=request.session['customer_id'], isRead=False
            ).count()
        elif user_type == 'vendor' and request.session.get('vendor_id'):
            count = Notification.objects.filter(
                vendorID_id=request.session['vendor_id'], isRead=False
            ).count()
    except Exception:
        pass
    return {'unread_notif_count': count}
