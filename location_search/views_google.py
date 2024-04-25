import os

import requests
from django.shortcuts import redirect
from django.shortcuts import render

from station_tracker.models import Gas_Station
from .models import Search


# Submit on main page, updates search and is the core of functionality
def map_submit(request):
    if request.method == 'POST':
        # This is where you handle the POST request and save data to your database
        search = request.POST.get('location', '')
        range = request.POST.get('range', '')
        fuelType = request.POST.get('gasType', '')
        searchPref = request.POST.get('preferenceSelect', '')

        search = Search(location=search, range=range, fuelType=fuelType, searchPref=searchPref)
        search.save()

        my_secret = os.environ['api_key']

        locationInfo = geocode(search, my_secret)

        if locationInfo['results']:
            print(
                "#########################################################################################################################################################################################################################################################################")
            lat_lng = locationInfo['results'][0]['geometry']['location']

            # Convert miles to meters and then pass to the API make database entries
            apiRange = (convToRange(range) * 1609.34) / 2
            gas_station_database(request, lat_lng, apiRange, my_secret)

        return render(request, 'search_google.html', get_map_data_with_search_data(request, search, range, searchPref))


# TBH im not entirely sure what this does
def map_get(request):
    map_context = get_map_data(request)
    return render(request, 'search_google.html', map_context)


# Price Update method
def updatePrice(request, gas_station_id):
    gas_station = Gas_Station.objects.get(id=gas_station_id)
    print(gas_station_id)

    if request.method == 'POST':
        U80 = request.POST.get('regular_gas_price', '')
        U85 = request.POST.get('premium_gas_price', '')
        Diesel = request.POST.get('diesel_price', '')

        # Get the gas station from the database
        gas_station = Gas_Station.objects.get(id=gas_station_id)

        gas_station.regular_gas_price = U80
        gas_station.premium_gas_price = U85
        gas_station.diesel_price = Diesel

        # Save the gas station
        gas_station.save()

        return redirect('findGas')

    # If the request method is not POST, render the updatePrice.html template
    context = {"gas_station": gas_station}
    return render(request, 'updatePrice.html', context)


def geocode(address, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key,
    }
    response = requests.get(base_url, params=params)
    return response.json()


# Gets nearby gas stations
def nearby_gas_search(location, radius, api_key):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    location = f"{location['lat']},{location['lng']}"
    params = {
        "location": location,
        "radius": (radius * 1609.34)/2, # Convert to Miles
        "type": "gas_station",
        "key": api_key,
    }
    response = requests.get(base_url, params=params)
    return response.json()


def gas_station_database(request, location, radius, api_key):
    # Get data from the Google Places API
    data = nearby_gas_search(location, radius, api_key)

    # Iterate over each result in the data
    for result in data['results']:
        # Check if a GasStation object with the same station_name and address already exists
        try:
            gas_station = Gas_Station.objects.get(station_name=result['name'], address=result['vicinity'])
        except Gas_Station.DoesNotExist:
            # If it doesn't exist, create a new GasStation object
            gas_station = Gas_Station(
                station_name=result['name'],
                address=result['vicinity'],
                latitude=result['geometry']['location']['lat'],
                longitude=result['geometry']['location']['lng'],

            )

            # Save the GasStation object to the database
            gas_station.save()


# Initital map rendering
# returns render
def get_map_data(request):
    # get the map data with the inital/default values
    return get_map_data_with_search_data(request, request.session.get('location', 'Colorado Springs'), '5 Miles', '')


# returns dictionary
def get_map_data_with_search_data(request, search, userRange, searchPref):
    context = {'GOOGLE_API_KEY': os.environ['api_key']}

    location = search
    request.session['location'] = str(location)

    # Get lattitude and longitude from google maps api
    my_secret = os.environ['api_key']
    locationInfo = geocode(location, my_secret)
    lat_lng = locationInfo['results'][0]['geometry']['location']

    # Now add everything to the context so we can use it on the map
    context['map_lat'] = lat = lat_lng['lat']
    context['map_lng'] = lat_lng['lng']
    context['stations'] = [
            {
                'station_name': result['name'],
                'address': result['vicinity'],
                'latitude': result['geometry']['location']['lat'],
                'longitude': result['geometry']['location']['lng']
            }
            for result in nearby_gas_search(locationInfo['results'][0]['geometry']['location'], convToRange(userRange), my_secret)['results']
        ]


    return context


def convToRange(userRange):
    if userRange == '2.5 Miles':
        return 2.5
    elif userRange == '5 Miles':
        return 5
    elif userRange == '20 Miles':
        return 20
    else:
        return 5
