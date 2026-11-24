from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('search/', views.search_flights, name='search_flights'),

    path('register/', views.register, name='register'),

    path('login/', views.user_login, name='login'),

    path('logout/', views.user_logout, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('book/<int:flight_id>/',views.book_flight,name='book_flight'),

]