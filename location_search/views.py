from . import models
from django.shortcuts import render
import requests
from django.views.generic.edit import UpdateView,CreateView
from .forms import SearchForm
from django.shortcuts import render, redirect
from .models import Search
from django.shortcuts import render, get_object_or_404, get_list_or_404
from geopy.geocoders import Nominatim
from geopy.distance import Geodesic
import folium
from folium import IFrame
from .forms import SearchForm
from django.http import HttpResponse, HttpResponseRedirect
from station_tracker.models import Gas_Station
import os





#Submit on main page, updates search and is the core of functionality
def submit(request):
    if request.method == 'POST':
        # This is where you handle the POST request and save data to your database
        search = request.POST.get('location', '')
        range = request.POST.get('range', '')
        fuelType = request.POST.get('gasType', '')
        searchPref = request.POST.get('preferenceSelect', '')

        search = Search(location=search,range = range, fuelType = fuelType, searchPref = searchPref)
        search.save()

        my_secret = os.environ['api_key']
        
        locationInfo = geocode(search,my_secret)
        
        if locationInfo['results']:
            print("#########################################################################################################################################################################################################################################################################")
            lat_lng = locationInfo['results'][0]['geometry']['location']
        


        #Convert miles to meters and then pass to the API make database entries
            apiRange = (convToRange(range) * 1609.34)/2
            gas_station_database(request, lat_lng, apiRange,my_secret)
            request.session['map_context'] = map_viewSubmit(request, search, range,searchPref)

        
        
    return redirect("searchPage")    


#TBH im not entirely sure what this does
def searchPage(request):
    

    map_context = request.session.get('map_context', {})

    my_secret = os.environ['api_key']

    map_context['GOOGLE_API_KEY'] = my_secret

    return render(request,'stuff.html', map_context)


#Price Update method
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
    context = {"gas_station":gas_station}
    return render(request, 'updatePrice.html',context)

   
    

#############################################
#Google maps API functions
def my_view(request):
    context = {'GOOGLE_API_KEY': os.environ['api_key']}
    return render(request, 'stuff.html', context)


def geocode(address, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key,
    }
    response = requests.get(base_url, params=params)
    return response.json()
#Gets nearby gas stations
def nearby_gas_search(location,radius, api_key):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    location = f"{location['lat']},{location['lng']}"
    params = {
        "location": location,
        "radius": radius,
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

#Initital map rendering 
#returns render
def map_view(request):
    
    geolocator = Nominatim(timeout=10, user_agent="Fuel Buddy")
    location = 'Colorado'
    
    stations =  Gas_Station.objects.all()

    #Default location co springs, else location is the last search location
    location = request.session.get('location', 'Colorado Springs')
    
    #Convert adress to latttitude and longitude
    my_secret = os.environ['api_key']
    locationInfo = geocode(location,my_secret)
    lat_lng = locationInfo['results'][0]['geometry']['location']
    lat = lat_lng['lat']
    lng = lat_lng['lng']
    
    if location == 'Colorado':
        station_map = folium.Map(location=[lat, lng], zoom_start=8)
    else:
        station_map = folium.Map(location=[lat, lng], zoom_start=13)

    
    folium.Marker([lat, lng], icon = folium.Icon(color='red')).add_to(station_map)
    folium.Circle([lat, lng], radius=16090/2).add_to(station_map) # distance is in meters, multiply by 1609 for conversion to miles. 

    for station in stations:
        coords = (station.latitude, station.longitude)


        




        gas_station_id = Gas_Station.objects.get(station_name=station.station_name, address=station.address)
        #Mark each gas station with marker and popup with station name and link to  google maps
        icon_text = station.regular_gas_price

        folium.Marker(coords, tooltip = station.station_name + ": "+ station.address, popup = folium.Popup(f"<a href = http://maps.google.com/?q={station.address.replace(' ', '+')}>Directions</a><a href='updatePrice/{gas_station_id.id}' class='btn' target='_top'>Update gas prices</a><p>U-80: {station.regular_gas_price}</p><p>U-85: {station.premium_gas_price}</p><p>Diesel: {station.diesel_price}</p>"
         ),icon = folium.DivIcon(html=f"""<div style="background-color: #3333cc;
        border-radius: 50%;
        color: white;
        font-weight: bolder;
        font-family: courier new;
        width: 30px;
        height: 30px;
        display: flex;
        justify-content: center;
        align-items: center;">{icon_text}</div>""")).add_to(station_map)

    context = {'map': station_map._repr_html_()}

    my_secret = os.environ['api_key']

    context['GOOGLE_API_KEY'] = my_secret
    
    return render(request, 'stuff.html', context)


#After search rendering
#returns dictionary
def map_viewSubmit(request, search, userRange, searchPref):

    geolocator = Nominatim(timeout=10, user_agent="Fuel Buddy")
    location = 'Colorado'

    stations =  Gas_Station.objects.all()

    location = search 

    request.session['location'] = str(location)

    #Get lattitude and longitude from google maps api
    my_secret = os.environ['api_key']
    locationInfo = geocode(location,my_secret)
    lat_lng = locationInfo['results'][0]['geometry']['location']
    lat = lat_lng['lat']
    lng = lat_lng['lng']
    
    if location == 'Colorado':
        station_map = folium.Map(location=[lat, lng], zoom_start=8)
    else:
        station_map = folium.Map(location=[lat, lng], zoom_start=13)

    #Convert user string to int, and convert it to meters
    range = convToRange(userRange) * 1609


    folium.Marker([lat, lng], icon = folium.Icon(color='red')).add_to(station_map)
    folium.Circle([lat, lng], radius=range/2).add_to(station_map)
                  # distance is in meters, multiply by 1609 for conversion to miles.
    

    for station in stations:
        
        coords = (station.latitude, station.longitude)

        icon_text = ""

        #Updates each marker with chosen gas prices
        if searchPref == 'Unleaded' and station.regular_gas_price is not None:
            icon_text = station.regular_gas_price
        elif searchPref == 'Premium' and station.premium_gas_price is not None:
            icon_text = station.premium_gas_price
        elif searchPref == 'Diesel' and station.diesel_price is not None:
            icon_text = station.diesel_price
        else:
            icon_text = 'N/A'  
        
        
        
        
        gas_station_id = Gas_Station.objects.get(station_name=station.station_name, address=station.address)
        #Mark each gas station with marker and popup with station name and link to  google maps


        folium.Marker(coords, tooltip = station.station_name + ": "+ station.address, popup = folium.Popup(f"<a href = http://maps.google.com/?q={station.address.replace(' ', '+')}>Directions</a><a href='updatePrice/{gas_station_id.id}' class='btn' target='_top'>Update gas prices</a><p>Unleaded: {station.regular_gas_price}</p><p>Premium: {station.premium_gas_price}</p><p>Diesel: {station.diesel_price}</p>"
         ),icon = folium.DivIcon(html=f"""<div style="background-color: #3333cc;
        border-radius: 50%;
        color: white;
        font-weight: bolder;
        font-family: courier new;
        width: 30px;
        height: 30px;
        display: flex;
        justify-content: center;
        align-items: center;">{icon_text}</div>""")).add_to(station_map)


    context = {'map': station_map._repr_html_()}
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


