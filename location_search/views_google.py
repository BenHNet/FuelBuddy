import json
import os

import numpy
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

        return render(request, 'search_google.html', get_map_data_with_search_data(request, search, range, searchPref))


# TBH im not entirely sure what this does
def map_get(request):
    map_context = get_map_data(request)
    return render(request, 'search_google.html', map_context)


# Price Update method
def updatePrice(request, gas_station_location):
    location = gas_station_location.split("+")
    gas_station = Gas_Station.objects.get(latitude=location[0], longitude=location[1])

    if request.method == 'POST':
        gas_station.regular_gas_price = request.POST.get('regular_gas_price', '')
        gas_station.premium_gas_price = request.POST.get('premium_gas_price', '')
        gas_station.diesel_price = request.POST.get('diesel_price', '')

        # Save the gas station
        gas_station.save()

        return redirect('findGas')

    # If the request method is not POST, render the updatePrice.html template
    context = {"gas_station": gas_station,
               "url_param": numpy.format_float_positional(gas_station.latitude) + '+' + numpy.format_float_positional(
                   gas_station.longitude)}
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
        "radius": (radius * 1609.34) / 2,  # Convert to Miles
        "type": "gas_station",
        "key": api_key,
    }
    response = requests.get(base_url, params=params)
    return response.json()


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

    # Search Google for the gas stations
    data = nearby_gas_search(locationInfo['results'][0]['geometry']['location'], convToRange(userRange), my_secret)[
        'results']

    stations = []
    # Iterate over each result in the data and save it to the DB and merge the results
    # from Google and the DB
    for result in data:
        # Check if a GasStation object with the same station_name and address already exists
        try:
            gas_station = Gas_Station.objects.get(latitude=result['geometry']['location']['lat'],
                                                  longitude=result['geometry']['location']['lng'])
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

        stations.append({
            "station_name": result['name'],
            "address": result['vicinity'],
            "latitude": result['geometry']['location']['lat'],
            "longitude": result['geometry']['location']['lng'],
            "icon": result['icon'],
            "icon_background_color": result['icon_background_color'],
            "icon_mask_base_uri": result['icon_mask_base_uri'],
            "business_status": result['business_status'],
            "regular_gas_price": str(gas_station.regular_gas_price),
            "premium_gas_price": str(gas_station.premium_gas_price),
            "diesel_price": str(gas_station.diesel_price)
        })

    context['stations'] = json.dumps(stations)

    return context


def convToRange(userRange):
    if userRange == '2.5 Miles':
        return 2.5
    elif userRange == '5 Miles':
        return 5
    elif userRange == '7.5 Miles':
        return 7.5
    elif userRange == '10 Miles':
        return 10
    elif userRange == '15 Miles':
        return 15
    elif userRange == '20 Miles':
        return 20
    else:
        return 5
