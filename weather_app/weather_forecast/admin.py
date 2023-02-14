from django.contrib import admin
from .models import CityModel, WeatherModel, WeatherModelUser, CityUserModel

# Register your models here.

admin.site.register(CityModel)
admin.site.register(WeatherModel)
admin.site.register(WeatherModelUser)
admin.site.register(CityUserModel)
