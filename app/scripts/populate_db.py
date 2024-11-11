from django.contrib.auth.models import User
from app.models import Profile, Provider, Category, Service, Booking, Review
from decimal import Decimal
from django.utils.timezone import now, timedelta
import random


# Create Users and Profiles
def create_users_and_profiles():
    users_data = [
        {"username": f"user_{i}", "email": f"user{i}@example.com", "password": "password123", "first_name": f"User{i}", "last_name": "Test"} for i in range(1, 8)
    ] + [
        {"username": f"provider_{i}", "email": f"provider{i}@example.com", "password": "password123", "first_name": "Provider", "last_name": f"{i}"} for i in range(1, 4)
    ]

    profiles = []
    providers = []

    for user_data in users_data:
        user = User.objects.create_user(**user_data)
        profile = Profile.objects.create(user=user, phone="1234567890", location=f"City {random.randint(1, 5)}", wallet=Decimal("100.00"))
        profiles.append(profile)
        if user_data["username"].startswith("provider"):
            providers.append(Provider.objects.create(profile=profile, about="Experienced professional offering quality services.", contact_email=user.email))

    print(f"Created {len(profiles)} profiles and {len(providers)} providers.")


# Create Categories
def create_categories():
    categories_data = [
        {
            "name": "Graphic Design",
            "description": "Creative design services.",
            "icon": "fas fa-paint-brush"  # Example: Font Awesome icon class
        },
        {
            "name": "Writing & Translation",
            "description": "Writing and translation services.",
            "icon": "fas fa-pen-nib"
        },
        {
            "name": "Digital Marketing",
            "description": "Marketing services for businesses.",
            "icon": "fas fa-chart-line"
        },
        {
            "name": "Web Development",
            "description": "Website and web app creation.",
            "icon": "fas fa-code"
        },
        {
            "name": "Video Editing",
            "description": "Professional video editing services.",
            "icon": "fas fa-video"
        },
    ]

    categories = [Category(**data) for data in categories_data]
    Category.objects.bulk_create(categories)
    print(f"Created {len(categories)} categories.")


# Create Services
def create_services():
    providers = Provider.objects.all()
    categories = Category.objects.all()

    if not providers or not categories:
        print("Providers or Categories missing. Create them first.")
        return

    services = []
    for provider in providers:
        for category in categories:
            for _ in range(random.randint(1, 2)):  # Fewer services per provider per category
                services.append(Service(
                    provider=provider,
                    category=category,
                    title=f"{category.name} Service by {provider.profile.user.username}",
                    description=f"Top-quality {category.name.lower()} service provided by {provider.profile.user.username}.",
                    price=Decimal(random.randint(50, 150)),
                    duration=timedelta(hours=random.randint(1, 4)),
                    approval="approved",
                    is_active=True
                ))

    Service.objects.bulk_create(services)
    print(f"Created {len(services)} services.")


# Create Bookings
def create_bookings():
    customers = Profile.objects.exclude(provider__isnull=False)
    services = Service.objects.filter(is_active=True, approval='approved')

    if not customers or not services:
        print("Customers or Services missing. Create them first.")
        return

    bookings = []
    for customer in customers:
        for _ in range(random.randint(1, 5)):  # bookings per customer
            service = random.choice(services)
            bookings.append(Booking(
                service=service,
                customer=customer,
                scheduled_time=now() + timedelta(days=random.randint(1, 30)),
                details="Looking forward to this service!",
                status=random.choice(["pending", "in_progress", "completed", "cancelled"]),
                created_at=now(),
            ))

    Booking.objects.bulk_create(bookings)
    print(f"Created {len(bookings)} bookings.")


# Create Reviews
def create_reviews():
    bookings = Booking.objects.all()

    if not bookings:
        print("No bookings available to create reviews.")
        return

    reviews = []
    for booking in bookings:
        # Determine the likelihood of satisfaction
        is_satisfied = random.choices(
            [True, False],  # Outcomes
            weights=[70, 30],  # 70% chance of being satisfied, 30% chance of being dissatisfied
            k=1
        )[0]

        if is_satisfied:
            rating = Decimal(random.randint(4, 5))  # Positive ratings
            comment = random.choice([
                "Excellent service, very professional!",
                "Good experience overall, but could improve in some areas.",
                "Amazing quality and very responsive provider!",
            ])
        else:
            rating = Decimal(random.randint(1, 3))  # Negative or neutral ratings
            comment = random.choice([
                "Service was satisfactory but not exceptional.",
                "Not up to the mark, expected better.",
                "Disappointed with the service, would not recommend.",
            ])

        reviews.append(Review(
            provider=booking.service.provider,
            reviewer=booking.customer,
            rating=rating,
            comment=comment,
            created_at=now() - timedelta(days=random.randint(1, 30))
        ))

    Review.objects.bulk_create(reviews)
    print(f"Created {len(reviews)} reviews.")


# Main Entry Point
def run():
    """Required entry point for Django Extensions' `runscript` command."""
    print("Populating database...")
    create_users_and_profiles()
    create_categories()
    create_services()
    create_bookings()
    create_reviews()

    print("Database populated successfully!")
