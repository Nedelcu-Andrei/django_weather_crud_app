from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class CityModel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class WeatherModel(models.Model):
    city = models.ForeignKey(CityModel, on_delete=models.CASCADE)
    temperature = models.FloatField()  # in C
    feels_like = models.FloatField()  # in C
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.CharField(max_length=20)
    cloud = models.FloatField()
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city} {self.description}"


class WeatherModelUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    temperature = models.FloatField()  # in C
    feels_like = models.FloatField()  # in C
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.CharField(max_length=20)
    cloud = models.FloatField()
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user} {self.city}"


class CityUserModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, default='')

    def __str__(self):
        return self.city

