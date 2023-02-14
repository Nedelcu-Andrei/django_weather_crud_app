from django.contrib.auth.models import User
from .models import WeatherModel, CityModel, WeatherModelUser, CityUserModel
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import requests
import logging
from .forms import LoginForm, NewUserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.

# logger setup
logging.basicConfig(level=logging.ERROR)


######################## API'S USED/ENDPOINTS ########################

def get_weather(city_name: str):
    """
    Get the weather data from the API endpoint.
    """
    # Basic setup
    X_RAPIDAPI_KEY = 'f35859e6b9msh2b00341fe6c8786p14195djsn1e688ed63a07'
    X_RAPIDAPI_HOST = 'weatherapi-com.p.rapidapi.com'
    weather_endpoint = 'https://weatherapi-com.p.rapidapi.com/current.json'

    # Request
    headers = {
        "X-RapidAPI-Key": X_RAPIDAPI_KEY,
        "X-RapidAPI-Host": X_RAPIDAPI_HOST
    }
    query_string = {"q": city_name}

    try:
        res = requests.get(weather_endpoint, params=query_string, headers=headers)
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        raise SystemExit

    return res.json()


######################## MAIN APP DISPLAY ########################

def weather(request):
    """
    Parse and set the weather data in a context for the model.
    """
    if request.method == 'POST':
        city = request.POST['city']
        weather_data = get_weather(city)

        if not weather_data:
            return HttpResponse(f'Weather data not found for city {city}')

        context = {'city_name': city.capitalize(),
                   'temperature': f"{weather_data['current']['temp_c']} °C",
                   'feels_like': f"{weather_data['current']['feelslike_c']} °C",
                   'humidity': weather_data['current']['humidity'],
                   'wind_speed': weather_data['current']['wind_kph'],
                   'wind_direction': weather_data['current']['wind_dir'],
                   'cloud': f"{weather_data['current']['cloud']} %",
                   'description': weather_data['current']['condition']['text']}
    else:
        context = {}

    return render(request, 'weather_forecast/index.html', context)


def weather_to_db_view(request):
    if request.method == 'POST':
        weather_to_db = WeatherModelUser(user=request.user,
                                         city=request.POST['city'].capitalize(),
                                         temperature=float(request.POST['temperature'].replace("°C", "")),
                                         feels_like=float(request.POST['feels_like'].replace("°C", "")),
                                         humidity=request.POST['humidity'],
                                         wind_speed=request.POST['wind_speed'],
                                         wind_direction=request.POST['wind_direction'],
                                         cloud=float(request.POST['cloud'].replace("%", "")),
                                         description=request.POST['description'])
        weather_to_db.save()
        return render(request, 'weather_forecast/location_saved.html')


######################## USER DATABASE UPDATES ########################

def user_city_to_db_view(request):
    """
    Method that checks if a city is already in the user's DB, else it saves it.
    """
    if request.method == 'POST':
        city_from_post = request.POST['city']

        city = CityUserModel.objects.filter(city=city_from_post)  # Check if location in DB
        if city:
            messages.warning(request, "City already in your database!. Please pick another city.")
            return render(request, 'weather_forecast/invalid_location_saved.html')

        city_to_db = CityUserModel(user=request.user,
                                   city=city_from_post)
        city_to_db.save()
        return render(request, 'weather_forecast/location_saved.html')


def saved_locations_view(request):
    """
    Method that that lists the user all his saved locations + Pagination.
    """
    user = request.user
    locations = CityUserModel.objects.filter(user=user)
    page_obj = pagination(request=request, data=locations, per_page=24)  # Pagination

    return render(request, 'weather_forecast/list_saved_locations.html', {'page_obj': page_obj})


def update_description_view(request, location_id):
    """
    Method to UPDATE a user's description for a saved location.
    """
    city = get_object_or_404(CityUserModel, pk=location_id)  # Check if location exists in DB
    if request.method == 'POST':
        city.description = request.POST['description']
        city.save()
        return redirect('http://127.0.0.1:8000/list_locations/')


def delete_location_view(request, location_id):
    """
    Method to DELETE a user's location from his locations list based on location ID.
    The location ID's do not update as the ID is from DB and it's not getting reused.
    """
    city = get_object_or_404(CityUserModel, pk=location_id)  # Check if location exists in DB
    if request.method == 'POST':
        city.delete()
        return redirect('http://127.0.0.1:8000/list_locations/')


def location_details_view(request, location_id):
    """
    Method that shows to user the details about a saved location.
    Uses the API request for the weather data.
    """
    city = get_object_or_404(CityUserModel, pk=location_id)  # Check if location exists in DB
    if request.method == 'POST':
        location = city.city
        location_user_description = city.description
        weather_data = get_weather(location)

        if not weather_data:
            return HttpResponse(f'Weather data not found for city {location}')

        weather_details = {
            'user_description': location_user_description,
            'id': location_id,
            'city_name': location,
            'temperature': f"{weather_data['current']['temp_c']} °C",
            'feels_like': f"{weather_data['current']['feelslike_c']} °C",
            'humidity': weather_data['current']['humidity'],
            'wind_speed': weather_data['current']['wind_kph'],
            'wind_direction': weather_data['current']['wind_dir'],
            'cloud': f"{weather_data['current']['cloud']} %",
            'description': weather_data['current']['condition']['text'],
            'widget_temperature': weather_data['current']['temp_c'],
            'widget_rain': weather_data['current']['precip_mm']
        }
    else:
        weather_details = {}

    return render(request, 'weather_forecast/view_location_details.html', context=weather_details)


######################## AUTHENTICATION/LOGIN/LOGOUT ########################

def register_view(request):
    """
    Method used to register a new user. Validations checked based on form.
    """
    if request.method == "POST":
        form = NewUserForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("http://127.0.0.1:8000/dashboard/")  # Return to dashboard

        messages.error(request, get_error_messages(form=form))
        return redirect("http://127.0.0.1:8000/register/")  # To not show error msg on refresh

    form = NewUserForm()
    return render(request, 'weather_forecast/register.html', context={"form": form})


def login_view(request):
    """
    Method used to login a user. Validations checked based on default AuthenticationForm form.
    """
    if request.method == 'POST':
        form = LoginForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('http://127.0.0.1:8000/dashboard/')

        messages.error(request, get_error_messages(form))

    form = LoginForm()
    return render(request, 'weather_forecast/login.html', context={'form': form})


def logout_view(request):
    """
    Method used to logout a user.
    """
    logout(request)
    return render(request, 'weather_forecast/logout.html')


######################## HELPER FUNCTIONS ########################

def get_error_messages(form):
    """
    Parse the json errors from the forms to send only the message to the user.
    """
    errors = form.errors.get_json_data()
    for field in errors:
        for error in errors[field]:
            return error['message']


def pagination(*, request, data, per_page: int):
    """
    Method used for pagination. Implied spelling for clear understanding.
    """
    paginator = Paginator(data, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj




