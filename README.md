# Travel App Project Setup Guide

This guide covers the setup and configuration of listings application with models, serializers, and sample data seeding.

## Project Structure

```
alx_travel_app_0x00/
├── alx_travel_app/
│   ├── settings.py
│   └── ...
├── listings/
│   ├── models.py
│   ├── serializers.py
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed.py
│   └── ...
└── manage.py
```

## Models Overview

The application includes four main models:

- **User**: Extended Django user model
- **Listing**: Property listings with title, description, price, and availability dates
- **Booking**: User bookings for specific listings with start/end dates
- **Review**: User reviews for listings with ratings and comments

## Setup Instructions

### 1. Create and Apply Migrations

First, create migrations for your listings models:

```bash
python manage.py makemigrations listings
```

Apply the migrations to create database tables:

```bash
python manage.py migrate
```

### 2. Directory Structure for Management Commands

Create the required directory structure for the seed command:

```bash
mkdir -p listings/management/commands
touch listings/management/__init__.py
touch listings/management/commands/__init__.py
```

### 3. Seed Database with Sample Data

Run the seed command to populate your database with sample data:

```bash
python manage.py seed
```

This command will create:
- 8 sample users with realistic names and credentials
- 10 property listings with varied descriptions and prices ($75-$400/night)
- 6 sample bookings with random date ranges
- 3 sample reviews with ratings and comments

### 4. Verify Data Creation

You can verify the data was created successfully by checking the command output or using the Django shell:

```bash
python manage.py shell
```

```python
from listings.models import User, Listing, Booking, Review

print(f"Users: {User.objects.count()}")
print(f"Listings: {Listing.objects.count()}")
print(f"Bookings: {Booking.objects.count()}")
print(f"Reviews: {Review.objects.count()}")
```

## Sample Data Details

### Users
- Usernames: john_doe, jane_smith, mike_johnson, etc.
- Default password: `password123`
- All users have realistic first names, last names, and email addresses

### Listings
- Various property types: apartments, villas, cabins, lofts, etc.
- Price range: $75-$400 per night
- Random availability periods (60-300 days from today)
- Detailed descriptions for each property type

### Bookings
- Random booking periods (2-7 days)
- Bookings fall within listing availability windows
- Each booking links a user to a specific listing

### Reviews
- Ratings: 4-5 stars (mostly positive reviews)
- Realistic review comments
- Each review links to both a user and a listing

## Model Relationships

- **User** ↔ **Booking**: One-to-many (user can have multiple bookings)
- **User** ↔ **Review**: One-to-many (user can write multiple reviews)
- **Listing** ↔ **Booking**: One-to-many (listing can have multiple bookings)
- **Listing** ↔ **Review**: One-to-many (listing can have multiple reviews)

## API Serializers

The application includes DRF serializers for all models:

- **UserSerializer**: Handles user data serialization
- **ListingSerializer**: Handles property listing data
- **BookingSerializer**: Includes nested user and listing data
- **ReviewSerializer**: Includes nested user and listing data

## Development Notes

### Clearing Data

The seed command automatically clears existing data before creating new records. This includes:
- All reviews
- All bookings  
- All listings
- All non-superuser users

### Customizing Sample Data

To modify the sample data, edit the data arrays in `listings/management/commands/seed.py`:
- `user_data`: User information
- `listings_data`: Property details and prices
- `reviews_data`: Review ratings and comments

### Password Information

All seeded users use the password `password123` for development purposes. Remember to use secure passwords in production environments.

## Next Steps

After completing the setup:

1. Create Django REST Framework views for your models
2. Configure URL patterns for your API endpoints
3. Add authentication and permissions as needed
4. Implement frontend components to display and interact with the data
5. Add validation and business logic to your models and serializers

## Troubleshooting

### Migration Issues
If you encounter migration errors:
```bash
python manage.py makemigrations --empty listings
python manage.py migrate
```

### Seed Command Not Found
Ensure the management command directory structure exists and includes `__init__.py` files.

### Database Errors
Verify that migrations have been applied before running the seed command.