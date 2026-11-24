from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class Airport(models.Model):

    name = models.CharField(max_length=150)

    city = models.CharField(max_length=100)

    code = models.CharField(max_length=3, unique=True)

    country = models.CharField(max_length=100, default="India")

    def __str__(self):
        return f"{self.city} ({self.code})"

class Meta:
    ordering = ['city']


class Airline(models.Model):

    name = models.CharField(max_length=150)

    code = models.CharField(max_length=3, unique=True)

    logo = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Flight(models.Model):

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    flight_number = models.CharField(
        max_length=20,
        unique=True
    )

    airline = models.ForeignKey(
        Airline,
        on_delete=models.PROTECT,
        related_name='flights'
    )

    source = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name='departing_flights'
    )

    destination = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name='arriving_flights'
    )

    departure_time = models.DateTimeField()

    arrival_time = models.DateTimeField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    total_seats = models.PositiveIntegerField(
        default=180
    )

    available_seats = models.PositiveIntegerField(
        default=180
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def clean(self):

        if self.source_id and self.destination_id:
            if self.source_id == self.destination_id:
                raise ValidationError(
                    "Departure and arrival airports must differ."
                )

            if self.departure_time and self.arrival_time:
                if self.arrival_time <= self.departure_time:
                    raise ValidationError(
                        "Arrival must be after departure."
                    )

                if self.available_seats > self.total_seats:
                    raise ValidationError(
                        "Available seats cannot exceed total seats."
                    )

    def __str__(self):
        return f"{self.flight_number} - {self.source.city} to {self.destination.city}"

class Meta:
    ordering = ['departure_time']
    indexes = [
        models.Index(
            fields=['source', 'destination', 'departure_time']
        ),
        models.Index(fields=['status']),
    ]


class Booking(models.Model):

    BOOKING_STATUS = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='flight_bookings'
    )

    flight = models.ForeignKey(
        Flight,
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    pnr = models.CharField(
        max_length=12,
        unique=True,
        editable=False
    )

    passengers_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)]
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    booking_status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default='pending'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='unpaid'
    )

    booking_date = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        if not self.pnr:
            self.pnr = uuid.uuid4().hex[:10].upper()
            super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.pnr} - {self.user.username}"

class Meta:
    ordering = ['-booking_date']


class Passenger(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='passengers'
    )

    full_name = models.CharField(max_length=150)

    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)]
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    seat_number = models.CharField(
        max_length=5,
        blank=True
    )

    def __str__(self):
        return self.full_name