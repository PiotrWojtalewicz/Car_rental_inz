from django.urls import path
from . import views
from .views import login_view, logout_view
from django.contrib.auth import views as auth_views
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
]
