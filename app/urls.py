from django.urls import path
from . import views
from .views import login_view, logout_view
from django.contrib.auth import views as auth_views
from .views import user_dashboard,rental_history,available_cars
urlpatterns = [
    path('', views.home, name='home'),  # Domyślny widok
    # Widoki dotyczące samochodów
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/add/', views.car_create, name='car_create'),
    path('cars/<int:car_id>/edit/', views.car_update, name='car_update'),
    path('cars/<int:car_id>/delete/', views.car_delete, name='car_delete'),
    #widoki logowania
    path('register/', views.register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    #widoki potrzebne do resetowania hasła
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('dashboard/', user_dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='profile'),
    path('rental-history/', rental_history, name='rental_history'),
    path('available-cars/', available_cars, name='available_cars'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('rentals/', views.user_rentals, name='rental_history'),
    path('add_car/', views.add_car, name='add_car'),


    #admin
    # path('admin/add_car/', views_admin.add_car, name='add_car'),
    # path('admin/car/<int:car_id>/update/', views_admin.car_update, name='car_update'),
    # path('admin/car/<int:car_id>/delete/', views_admin.car_delete, name='car_delete'),
    # path('admin/add_representative/', views_admin.add_representative, name='add_representative'),
    # path('admin/cars/', views_admin.car_list, name='car_list'),
    # path('admin/car/<int:car_id>/', views_admin.car_detail, name='car_detail'),
    # path('admin/car/<int:car_id>/assign_representative/', views_admin.assign_representative,
    #      name='assign_representative'),

    #możliwośc wypożyczenia samochodu
    path('availability/', views.availability_calendar, name='availability_calendar'),
    path('rent_car/<int:car_id>/', views.rent_car, name='rent_car'),
    #warunki umowy
    # path('rent_car/<int:car_id>/', views.rent_car, name='rent_car'),
    path('terms_conditions/', views.terms_conditions, name='terms_conditions'),
    path('rent_car/<int:car_id>/', views.rent_car, name='rent_car'),
    #płatność
    path('reservation_summary/<int:car_id>/', views.reservation_summary, name='reservation_summary'),
    path('payment/<int:rental_id>/', views.payment_view, name='payment_view'),
    #kalendarz
    # path('car/<int:car_id>/rental/', views.car_rental, name='car_rental'),
    # path('rental/confirmation/<int:rental_id>/', views.rental_confirmation, name='rental_confirmation'),
    #widoki po wyborze metody płatności
    path('payment_card/<int:car_id>/', views.payment_card, name='payment_card'),
    path('payment_bank/<int:car_id>/', views.payment_bank, name='payment_bank'),
    path('payment_paypal/<int:car_id>/', views.payment_paypal, name='payment_paypal'),
    path('payment_cash/<int:car_id>/', views.payment_cash, name='payment_cash'),
    path('rentals/extend/<int:rental_id>/', views.extend_rental, name='extend_rental'),
    # path('rentals/extend/<int:rental_id>/', views.extend_rental, name='extend_rental'),
    path('payment_success/', views.payment_success, name='payment_success'),

]
