from datetime import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

from .models import Flight, Booking, Passenger
from .forms import RegistrationForm


# Home Page
def home(request):
    return render(request, 'flights/index.html')


# Search Flights
def search_flights(request):

    if request.method != 'GET' or not request.GET:
        return render(request, 'flights/index.html')

    source = request.GET.get('source', '').strip()
    destination = request.GET.get('destination', '').strip()
    departure = request.GET.get('departure', '').strip()
    passengers = request.GET.get('passengers', '1')
    trip_type = request.GET.get('trip_type', 'one-way')

    context = {
        'source': source,
        'destination': destination,
        'departure': departure,
        'passengers': passengers,
        'trip_type': trip_type,
    }

    if not source or not destination or not departure:
        context['error'] = 'Please fill in all required fields.'
        return render(request, 'flights/results.html', context)

    if source.lower() == destination.lower():
        context['error'] = 'Source and destination cannot be the same.'
        return render(request, 'flights/results.html', context)

    try:
        passenger_count = int(passengers)

        if passenger_count < 1 or passenger_count > 9:
            raise ValueError

    except (ValueError, TypeError):
        context['error'] = 'Passenger count must be between 1 and 9.'
        return render(request, 'flights/results.html', context)

    try:
        departure_date = datetime.strptime(
            departure, '%Y-%m-%d'
        ).date()

        if departure_date < timezone.localdate():
            context['error'] = 'Please select today or a future date.'
            return render(request, 'flights/results.html', context)

    except ValueError:
        context['error'] = 'Please enter a valid departure date.'
        return render(request, 'flights/results.html', context)

    flights = Flight.objects.filter(
        source__city__iexact=source,
        destination__city__iexact=destination,
        departure_time__date=departure_date,
        available_seats__gte=passenger_count,
        status='scheduled',
        departure_time__gte=timezone.now()
    ).select_related(
        'airline',
        'source',
        'destination'
    )

    sort_by = request.GET.get('sort', 'price')

    if sort_by == 'departure':
        flights = flights.order_by('departure_time')

    elif sort_by == 'arrival':
        flights = flights.order_by('arrival_time')

    else:
        sort_by = 'price'
        flights = flights.order_by('price')

        # This section must be OUTSIDE the sorting conditions.
        context.update({
            'flights': flights,
            'flight_count': flights.count(),
            'passenger_count': passenger_count,
            'sort_by': sort_by,
            'search_completed': True,
        })

        return render(request, 'flights/results.html', context)


    # User Registration
def register(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                'Your QuickSky account has been created successfully!'
            )

            return redirect('dashboard')

        else:
            form = RegistrationForm()

            return render(
                request,
                'flights/register.html',
                {'form': form}
            )


        # User Login
def user_login(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(
                request,
                f'Welcome back, {user.first_name or user.username}!'
            )

            next_url = request.POST.get('next') or request.GET.get('next')

            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)

            return redirect('dashboard')

        else:
            form = AuthenticationForm()

            return render(
                request,
                'flights/login.html',
                {'form': form}
            )


        # User Logout
@login_required
def user_logout(request):

    if request.method == 'POST':
        logout(request)

        messages.success(
            request,
            'You have successfully logged out.'
        )

        return redirect('home')

    return redirect('dashboard')


# User Dashboard
@login_required
def dashboard(request):

    return render(
        request,
        'flights/dashboard.html',
        {'user': request.user}
    )


# Book a Flight
@login_required(login_url='login')
def book_flight(request, flight_id):

    flight = get_object_or_404(Flight, pk=flight_id)

    # Get passenger count
    try:
        passenger_count = int(
            request.POST.get(
                'passenger_count',
                request.GET.get('passengers', '1')
            )
        )

        if passenger_count < 1 or passenger_count > 9:
            raise ValueError

    except (ValueError, TypeError):
        passenger_count = 1

        # Initialize context
        context = {
            'flight': flight,
            'passenger_count': passenger_count,
            'passenger_rows': range(1, passenger_count + 1),
        }

        # Process passenger form
        if request.method == 'POST':

            passenger_data = []

            # Collect and validate passenger details
            for i in range(1, passenger_count + 1):

                name = request.POST.get(
                    f'passenger_name_{i}', ''
                ).strip()

                age = request.POST.get(
                    f'passenger_age_{i}', ''
                )

                gender = request.POST.get(
                    f'passenger_gender_{i}', ''
                )

                if not name:
                    context['error'] = f'Enter passenger {i} name.'
                    break

                try:
                    age = int(age)

                    if age < 1 or age > 120:
                        raise ValueError

                except (ValueError, TypeError):
                    context['error'] = f'Enter a valid age for passenger {i}.'
                    break

                if gender not in ['male', 'female', 'other']:
                    context['error'] = f'Select a valid gender for passenger {i}.'
                    break

                passenger_data.append({
                    'full_name': name,
                    'age': age,
                    'gender': gender,
                })

                # Check validation errors AFTER the loop
                if 'error' in context:
                    return render(request, 'flights/book_flight.html', context)

                # Create booking
                try:

                    with transaction.atomic():

                        locked_flight = Flight.objects.select_for_update().get(
                            pk=flight_id
                        )

                        if locked_flight.status != 'scheduled':
                            raise ValueError(
                                'This flight is not available.'
                            )

                        if locked_flight.departure_time <= timezone.now():
                            raise ValueError(
                                'This flight has already departed.'
                            )

                        if locked_flight.available_seats < passenger_count:
                            raise ValueError(
                                'Not enough seats are available.'
                            )

                        booking = Booking.objects.create(
                            user=request.user,
                            flight=locked_flight,
                            passengers_count=passenger_count,
                            total_amount=(
                                locked_flight.price * passenger_count
                            ),
                        )

                        Passenger.objects.bulk_create([
                            Passenger(
                                booking=booking,
                                full_name=p['full_name'],
                                age=p['age'],
                                gender=p['gender'],
                            )
                            for p in passenger_data
                        ])

                        # Reduce available seats
                        locked_flight.available_seats -= passenger_count

                        locked_flight.save(
                            update_fields=['available_seats']
                        )

                        # Successful booking
                        return render(request, 'flights/booking_confirmation.html', {'booking': booking})

                except ValueError as e:

                    context['error'] = str(e)

                    # Display booking form
                    return render(request, 'flights/book_flight.html', context)