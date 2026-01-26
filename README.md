# 🎵 Vinyl Store - Full-Stack E-Commerce Platform

A complete university capstone project implementing a full-stack online vinyl record store. Built with **Django**, **PostgreSQL/SQLite**, and responsive **HTML/CSS/JavaScript**.

## 📋 Project Overview

The Vinyl Store is a multi-role e-commerce platform where:
- **Customers** can browse, search, and purchase vinyl records
- **Vendors** can manage their stores and products
- **Admins** can manage all system data via Django admin
- **Features** include cart management, orders, reviews, wishlists, and promotions

## 🏗️ Architecture

### Tech Stack
- **Backend**: Django 5.2 (Python 3.x)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Django Templates + HTML5 + CSS3 + JavaScript
- **Authentication**: Django session-based with password hashing
- **Version Control**: Git

### Project Structure
```
vinyl_store/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── vinyl_config/                      # Main Django project settings
│   ├── settings.py                   # Configuration
│   ├── urls.py                       # URL routing
│   └── wsgi.py                       # Production entry point
├── store/                            # Main application
│   ├── models.py                     # All database models
│   ├── views.py                      # Business logic (1000+ lines)
│   ├── urls.py                       # Route definitions
│   ├── admin.py                      # Django admin configuration
│   ├── management/commands/          # Custom management commands
│   │   └── seed_data.py             # Populate sample data
│   ├── migrations/                   # Database migrations
│   ├── templates/store/              # HTML templates
│   │   ├── base.html                # Master template
│   │   ├── home.html                # Homepage
│   │   ├── customer_*.html          # Customer pages
│   │   ├── vendor_*.html            # Vendor pages
│   │   ├── product_*.html           # Product pages
│   │   ├── cart.html                # Shopping cart
│   │   ├── checkout.html            # Order checkout
│   │   └── order_*.html             # Order management
│   └── static/css/
│       └── style.css                # Complete styling (900+ lines)
└── media/                           # User uploads (product images)
```

## 🗄️ Database Models (14 Models)

1. **Customer** - User accounts for shoppers
2. **Vendor** - Seller accounts
3. **Store** - Vendor's storefront
4. **Product** - Vinyl records
5. **ProductMedia** - Product images/videos
6. **CartItem** - Shopping cart items
7. **Order** - Customer orders
8. **OrderItem** - Individual items in orders
9. **OrderStatus** - Order status tracking
10. **CancelledItem** - Cancellation records
11. **WishlistItem** - Saved products
12. **Promotion** - Discount campaigns
13. **Review** - Customer reviews & ratings
14. **ClickHistory** - Analytics tracking

### Key Relationships
- Customer ↔ Cart Items (1:N)
- Customer ↔ Orders (1:N)
- Vendor ↔ Store (1:1)
- Store ↔ Products (1:N)
- Product ↔ ProductMedia (1:N)
- Order ↔ OrderItems (1:N)
- OrderItem ↔ OrderStatus (1:N)
- Product ↔ Promotions (1:N)
- Customer ↔ Reviews (1:N)

## 🎯 Core Features

### Authentication & Authorization
- ✅ Customer registration & login
- ✅ Vendor registration & login
- ✅ Password hashing with Django's security
- ✅ Session-based authentication
- ✅ Role-based route protection

### Product Management
- ✅ Browse all products with pagination
- ✅ Search products by name/description
- ✅ Filter by store and price range
- ✅ Product detail pages with images
- ✅ Stock tracking and availability
- ✅ Multiple product images per listing
- ✅ Vendor product management dashboard

### Shopping Experience
- ✅ Add/remove items from cart
- ✅ Update quantities
- ✅ View cart with real-time totals
- ✅ Checkout process
- ✅ Order confirmation

### Orders & Fulfillment
- ✅ Create orders from cart
- ✅ Track order status (Processing → Shipping → Completed)
- ✅ View order history
- ✅ Order cancellation tracking
- ✅ Historical pricing (save price at purchase)

### Promotions & Pricing
- ✅ Apply percentage discounts to products
- ✅ Time-based promotion scheduling
- ✅ Display original & discounted prices
- ✅ Calculate totals with promotions

### Customer Engagement
- ✅ Write/read 5-star reviews
- ✅ Add products to wishlist
- ✅ View wishlist with saved prices
- ✅ View click history for analytics

### Admin Interface
- ✅ Full Django admin access
- ✅ Manage customers, vendors, products
- ✅ View orders and reviews
- ✅ Inline editing for related models

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone or extract the project:**
   ```bash
   cd /Users/eve/Desktop/schoolWork/vinyl_store
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Load sample data:**
   ```bash
   python manage.py seed_data
   ```

6. **Create admin user (optional):**
   ```bash
   python manage.py createsuperuser
   ```
   Follow prompts to create admin account.

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   - **Store**: http://127.0.0.1:8000/
   - **Admin**: http://127.0.0.1:8000/admin/

## 📝 Test Credentials

### Sample Customer
- **Email**: alice@example.com
- **Password**: testpass123

### Sample Vendor
- **Email**: vinyl.paradise@example.com
- **Password**: vendorpass123

### Admin
- Created with `createsuperuser` command

## 🔐 Security Features

- ✅ **Password Hashing**: Uses Django's PBKDF2 algorithm
- ✅ **CSRF Protection**: Django middleware on all forms
- ✅ **SQL Injection Prevention**: ORM queries (no raw SQL)
- ✅ **Session Security**: Secure session cookies
- ✅ **Input Validation**: Form validation + model constraints
- ✅ **Authentication Required**: Protected views for customers & vendors

## 📂 Key Files Overview

### Models (`store/models.py` - 500 lines)
- Comprehensive field documentation
- Validators for numerical ranges
- Helper methods (is_in_stock, is_active, etc.)
- Relationships with on_delete constraints
- Custom database table names

### Views (`store/views.py` - 1000+ lines)
- **Authentication Views**: register, login, logout
- **Product Views**: listing, detail, search, filtering
- **Cart Views**: add, remove, update, view
- **Order Views**: checkout, history, detail
- **Review Views**: create/update reviews
- **Wishlist Views**: toggle wishlist items
- **Vendor Views**: dashboard, product management, image upload

### Templates (`store/templates/store/` - 12 files)
- **base.html**: Master template with navigation
- **home.html**: Featured products showcase
- **product_list.html**: Searchable product catalog
- **product_detail.html**: Full product view with reviews
- **cart.html**: Shopping cart with item management
- **checkout.html**: Order form with summary
- **order_*.html**: Order tracking and history
- **vendor_dashboard.html**: Vendor control panel
- **wishlist.html**: Saved items view
- Authentication pages for customer/vendor

### Styling (`store/static/css/style.css` - 900+ lines)
- Responsive grid layouts
- Mobile-first design (480px, 768px breakpoints)
- CSS variables for theming
- Smooth animations and transitions
- Professional color scheme
- Form styling and validation states

## 📊 Database Schema

All tables use:
- **Auto-increment primary keys** (except composite keys)
- **Foreign key constraints** with cascade/protect rules
- **Unique constraints** on emails
- **Composite unique constraints** (e.g., customerID + productID)
- **Timestamps** for created/updated tracking

## 🎨 UI/UX Features

- Responsive grid for products (auto-fit columns)
- Mobile navigation with flex layout
- Alert messages with auto-close
- Status badges with color coding
- Form validation with error display
- Image galleries with thumbnail selection
- Empty state illustrations
- Smooth hover effects and transitions

## 🧪 Testing the Application

### Customer Flow
1. Register at `/customer/register/`
2. Login at `/customer/login/`
3. Browse products at `/products/`
4. View product detail at `/products/<id>/`
5. Add to cart via product detail
6. View cart at `/cart/`
7. Checkout at `/checkout/`
8. View order at `/orders/<id>/`
9. Leave review on product page
10. Manage wishlist at `/wishlist/`

### Vendor Flow
1. Register at `/vendor/register/`
2. Login at `/vendor/login/`
3. Access dashboard at `/vendor/dashboard/`
4. Add products with form
5. Edit products
6. Upload product images
7. View store statistics

### Admin Flow
1. Create superuser
2. Login at `/admin/`
3. Manage all models
4. View relationships and statistics
5. Filter and search records

## 🔧 Customization

### Add More Products
Edit `store/management/commands/seed_data.py` and add to `products_data` list.

### Change Colors
Edit CSS variables in `store/static/css/style.css`:
```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #e74c3c;
    /* ... */
}
```

### Modify Database
1. Update models in `store/models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`

## 📚 Code Quality

- **Modular Design**: Separation of concerns (models, views, templates)
- **Comprehensive Comments**: Every model and major view documented
- **DRY Principles**: Reusable base template, helper methods
- **Error Handling**: Try-catch blocks, validation checks
- **Performance**: Select_related, prefetch_related for queries
- **Standards**: PEP 8 compliant Python, semantic HTML

## 🚨 Known Limitations

- No payment gateway (simulated orders)
- No real-time notifications (no websockets)
- No multi-file upload (single image per form)
- No email verification
- No two-factor authentication
- Development-only setup (no production config)

## 📖 Features Explanation

### Promotion System
Promotions are time-based discounts. When viewing a product, the system checks if any active promotions exist for that product. The discount is automatically applied to the price display and cart calculations.

### Order Status Flow
Orders follow: `Processing` → `Holding` → `Shipping` → `Completed`. The status history is tracked in `OrderStatus` for each order item.

### Wishlist Tracking
Wishlist items store the price at the time of adding, allowing price comparison. Customers can see if items have increased or decreased in price.

### Stock Management
When an order is placed, stock is automatically decremented. The `availability` flag reflects whether a product is in stock.

## 🎓 Academic Notes

This project demonstrates:
- Full MVC architecture implementation
- Database normalization and relationships
- Authentication and authorization
- Form handling and validation
- File uploads and media management
- RESTful URL design
- Template inheritance
- Git version control
- Project documentation

## 📞 Support

For issues or questions about the project:
1. Check the code comments (extensively documented)
2. Review Django official documentation
3. Verify database migrations are applied
4. Clear browser cache if UI issues occur

---

**Built with ❤️ for Academic Excellence** | Django 5.2 | 2026
