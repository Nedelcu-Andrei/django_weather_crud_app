from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.weather, name='city_name'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('save_location/', views.user_city_to_db_view, name='save_location'),
    path('list_locations/', views.saved_locations_view, name='list_locations'),
    path('update_description/<int:location_id>/', views.update_description_view, name='update_description'),
    path('delete/<int:location_id>/', views.delete_location_view, name='delete'),
    path('details/<int:location_id>/', views.location_details_view, name='details')
]
