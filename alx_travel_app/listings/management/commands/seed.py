from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Review
from datetime import date, timedelta
import random
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    """Management command to populate the database with sample listings data."""
    
    help = 'Populate the database with sample listings data'

    def handle(self, *args, **options):
        """Execute the command to seed the database with sample data."""
        
        self.stdout.write("Starting to seed database...")

        self.stdout.write("Clearing existing data...")
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write("Creating users...")
        users = []
        user_data = [
            ("john_doe", "John", "Doe", "john@example.com"),
            ("jane_smith", "Jane", "Smith", "jane@example.com"),
            ("mike_johnson", "Mike", "Johnson", "mike@example.com"),
            ("sarah_wilson", "Sarah", "Wilson", "sarah@example.com"),
            ("david_brown", "David", "Brown", "david@example.com"),
            ("emma_davis", "Emma", "Davis", "emma@example.com"),
            ("chris_miller", "Chris", "Miller", "chris@example.com"),
            ("lisa_garcia", "Lisa", "Garcia", "lisa@example.com"),
        ]

        for username, first_name, last_name, email in user_data:
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first_name,
                last_name=last_name
            )
            users.append(user)

        self.stdout.write(f"Created {len(users)} users")

        self.stdout.write("Creating listings...")
        listings_data = [
            ("Cozy Downtown Apartment", "Perfect for couples looking for a romantic getaway with stunning city views.", 120),
            ("Luxury Beachfront Villa", "Ideal for families, featuring spacious rooms and direct beach access.", 350),
            ("Mountain Cabin Retreat", "A peaceful retreat surrounded by nature and hiking trails.", 180),
            ("Modern City Loft", "Contemporary design with high-end furnishings in the heart of downtown.", 200),
            ("Charming Country House", "Experience rural life in this authentic farmhouse with garden views.", 90),
            ("Stylish Studio", "Minimalist design perfect for solo travelers or couples.", 75),
            ("Spacious Family Home", "4-bedroom house ideal for large groups and extended stays.", 250),
            ("Lakeside Cottage", "Wake up to beautiful lake views in this cozy waterfront property.", 160),
            ("Historic Brownstone", "Stay in a piece of history with modern amenities and classic charm.", 140),
            ("Penthouse Suite", "Luxury living with panoramic city views and premium amenities.", 400),
        ]

        listings = []
        for title, description, price in listings_data:
            start_date = date.today() + timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(60, 300))
            
            listing = Listing.objects.create(
                title=title,
                description=description,
                price_per_night=Decimal(str(price)),
                available_from=start_date,
                available_to=end_date
            )
            listings.append(listing)

        self.stdout.write(f"Created {len(listings)} listings")

        self.stdout.write("Creating bookings...")
        booking_count = 0
        for i in range(6):
            listing = random.choice(listings)
            user = random.choice(users)
            
            start_date = listing.available_from + timedelta(days=random.randint(0, 30))
            end_date = start_date + timedelta(days=random.randint(2, 7))
            
            if end_date <= listing.available_to:
                Booking.objects.create(
                    listing=listing,
                    user=user,
                    start_date=start_date,
                    end_date=end_date
                )
                booking_count += 1

        self.stdout.write(f"Created {booking_count} bookings")

        self.stdout.write("Creating reviews...")
        reviews_data = [
            (5, "Amazing stay! Everything was perfect."),
            (4, "Great location and clean apartment. Would stay again."),
            (5, "Perfect for our weekend getaway. Highly recommended!"),
            (4, "Good value for money. Minor issues but overall pleasant."),
            (5, "Absolutely loved this place! Will book again."),
        ]

        review_count = 0
        for rating, comment in reviews_data[:3]:
            listing = random.choice(listings)
            user = random.choice(users)
            
            Review.objects.create(
                listing=listing,
                user=user,
                rating=rating,
                comment=comment
            )
            review_count += 1

        self.stdout.write(f"Created {review_count} reviews")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDatabase seeding completed!\n"
                f"Total Users: {User.objects.count()}\n"
                f"Total Listings: {Listing.objects.count()}\n"
                f"Total Bookings: {Booking.objects.count()}\n"
                f"Total Reviews: {Review.objects.count()}"
            )
        )