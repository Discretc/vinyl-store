from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from store.models import (
    Customer, Vendor, Store, Product, ProductMedia, Promotion, Review
)


class Command(BaseCommand):
    help = 'Populate the database with sample vinyl store data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Create sample customers
        customers_data = [
            ('Alice', 'Johnson', 'alice@example.com', '555-0101'),
            ('Bob', 'Smith', 'bob@example.com', '555-0102'),
            ('Carol', 'Williams', 'carol@example.com', '555-0103'),
            ('David', 'Brown', 'david@example.com', '555-0104'),
            ('Emma', 'Davis', 'emma@example.com', '555-0105'),
        ]

        customers = []
        for first, last, email, phone in customers_data:
            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={
                    'firstName': first,
                    'lastName': last,
                    'phoneNumber': phone,
                    'shippingAddress': f'{first} at 123 {last} St, City, ST 12345'
                }
            )
            if created:
                customer.set_password('testpass123')
                customer.save()
                self.stdout.write(self.style.SUCCESS(f'Created customer: {first} {last}'))
            customers.append(customer)

        # Create sample vendors and stores
        vendors_data = [
            ('Vinyl Paradise', 'vinyl.paradise@example.com', '555-1001', 'Your gateway to classic vinyl records'),
            ('Retro Beats', 'retro.beats@example.com', '555-1002', 'Curated selection of rare vinyl'),
            ('Groovy Tunes', 'groovy.tunes@example.com', '555-1003', 'Discover vinyl from every genre'),
        ]

        vendors = []
        for vendor_name, email, phone, store_desc in vendors_data:
            vendor, created = Vendor.objects.get_or_create(
                email=email,
                defaults={
                    'vendorName': vendor_name,
                    'phoneNumber': phone,
                }
            )
            if created:
                vendor.set_password('vendorpass123')
                vendor.save()
                self.stdout.write(self.style.SUCCESS(f'Created vendor: {vendor_name}'))

            store, created = Store.objects.get_or_create(
                vendorID=vendor,
                defaults={
                    'storeName': vendor_name,
                    'description': store_desc,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created store: {vendor_name}'))
            vendors.append(vendor)

        # Create sample products
        products_data = [
            ('The Dark Side of the Moon', 'Pink Floyd', 'A masterpiece of progressive rock. This iconic 1973 album features "Money", "Us and Them", and "Brain Damage".', Decimal('19.99'), 15),
            ('Abbey Road', 'The Beatles', 'The Beatles\' iconic 1969 album featuring "Come Together", "Something", and "Here Comes the Sun".', Decimal('18.99'), 12),
            ('Hotel California', 'Eagles', 'The Eagles\' 1976 album with the classic title track and hits like "New Kid in Town".', Decimal('17.99'), 10),
            ('Led Zeppelin IV', 'Led Zeppelin', 'The legendary 1971 album with the epic "Stairway to Heaven" and other rock classics.', Decimal('21.99'), 8),
            ('Rumours', 'Fleetwood Mac', 'The 1977 album that defined a generation with "Dreams", "Go Your Own Way", and "Silver Springs".', Decimal('18.99'), 14),
            ('Thriller', 'Michael Jackson', 'The best-selling album of all time (1982) with "Billie Jean", "Beat It", and "Thriller".', Decimal('20.99'), 20),
            ('Born to Run', 'Bruce Springsteen', 'The 1975 masterpiece featuring the title track and "Thunder Road".', Decimal('19.99'), 9),
            ('Nevermind', 'Nirvana', 'The 1991 album that launched grunge with "Smells Like Teen Spirit".', Decimal('16.99'), 11),
        ]

        products = []
        for i, (name, artist, desc, price, stock) in enumerate(products_data):
            product, created = Product.objects.get_or_create(
                productName=name,
                storeID=vendors[i % len(vendors)].store,
                defaults={
                    'description': f'{desc}\n\nArtist: {artist}',
                    'price': price,
                    'stockQuantity': stock,
                    'availability': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {name}'))
            products.append(product)

        # Create sample promotions
        for i, product in enumerate(products[:3]):  # Add promos to first 3 products
            promo, created = Promotion.objects.get_or_create(
                productID=product,
                defaults={
                    'discountRate': Decimal('10') if i % 2 == 0 else Decimal('15'),
                    'startDate': timezone.now() - timedelta(days=5),
                    'endDate': timezone.now() + timedelta(days=30),
                    'status': 'active',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created promotion for: {product.productName}'))

        # Create sample reviews
        for product in products[:5]:
            for customer in customers[:3]:
                Review.objects.get_or_create(
                    customerID=customer,
                    productID=product,
                    defaults={
                        'rating': random.randint(3, 5),
                        'comment': f'Great vinyl quality! Really enjoyed this {product.productName} album.',
                    }
                )

        self.stdout.write(self.style.SUCCESS('\n✓ Data seeding completed successfully!'))
        self.stdout.write('\nTest Login Credentials:')
        self.stdout.write('  Customer: alice@example.com / testpass123')
        self.stdout.write('  Vendor: vinyl.paradise@example.com / vendorpass123')
