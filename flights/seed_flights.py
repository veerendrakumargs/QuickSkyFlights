from flights.models import Airport, Airline, Flight
from django.utils import timezone
from datetime import timedelta

routes = [
    ("BLR", "BOM", "6E201", "6E", 4500, 2),
    ("BLR", "DEL", "AI501", "AI", 6500, 3),
    ("BLR", "MAA", "QP302", "QP", 3500, 4),
    ("BLR", "HYD", "SG401", "SG", 3200, 5),
    ("BOM", "DEL", "6E502", "6E", 5000, 6),
    ("MAA", "COK", "AI603", "AI", 4000, 2),
]

for source_code, destination_code, number, airline_code, price, days in routes:

    departure = timezone.now() + timedelta(days=days)

    departure = departure.replace(
        hour=8,
        minute=30,
        second=0,
        microsecond=0
    )

    flight, created = Flight.objects.get_or_create(
        flight_number=number,
        defaults={
            "airline": Airline.objects.get(code=airline_code),
            "source": Airport.objects.get(code=source_code),
            "destination": Airport.objects.get(code=destination_code),
            "departure_time": departure,
            "arrival_time": departure + timedelta(hours=2, minutes=30),
            "price": price,
            "total_seats": 180,
            "available_seats": 180,
            "status": "scheduled"
        }
    )

    print(f"{number}: {'Created' if created else 'Already exists'}")

    print("Sample flight seeding completed!")
