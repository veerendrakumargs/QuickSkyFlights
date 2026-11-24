
from django.contrib import admin
from .models import Airport, Airline, Flight, Booking, Passenger


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'code', 'country')
    search_fields = ('name', 'city', 'code')


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        'flight_number',
        'airline',
        'source',
        'destination',
        'departure_time',
        'arrival_time',
        'price',
        'available_seats',
        'status'
    )

    list_filter = ('status', 'airline')

    search_fields = (
        'flight_number',
        'source__city',
        'destination__city'
    )

    list_editable = ('price', 'status')


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'pnr',
        'user',
        'flight',
        'passengers_count',
        'total_amount',
        'booking_status',
        'payment_status',
        'booking_date'
    )

    list_filter = ('booking_status', 'payment_status')

    search_fields = ('pnr', 'user__username')

    inlines = [PassengerInline]


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'booking',
        'age',
        'gender',
        'seat_number'
    )

    search_fields = ('full_name', 'booking__pnr')
