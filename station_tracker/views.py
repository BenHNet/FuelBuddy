from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserCreationForm, LoginForm, GasPriceUpdateForm, FeedbackForm, Feedback
from .models import Customer, GasStationOwner, Feedback, AboutUs, Gas_Station
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from geopy.geocoders import Nominatim
from geopy.distance import Geodesic
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
import folium

# Create your views here.
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_manage(request):
    feedback_list = Feedback.objects.all()
    if request.method == 'POST':
        if 'delete_feedback' in request.POST:
            feedback_id = request.POST.get('delete_feedback')
            Feedback.objects.filter(id=feedback_id).delete()
            return redirect('admin_manage')

    return render(request, 'station_tracker/admin_manage.html', {'feedback_list': feedback_list})
# Home page
def index(request):
  # Retrieve user information
  user = request.user

  # Pass user information to the template
  context = {'user': user}
  return render(request, 'index.html', context)

# signup page
def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
           # username = form.cleaned_data.get('username')
           # messages.success(request, f'Your account has been created! You are now able to log in') 
           # Check if the 'customer' checkbox is selected
            if 'customer' in request.POST:
                Customer.objects.create(user=user)
                messages.success(request, 'Account created as a customer.')
           # Check if the 'gas_station_owner' checkbox is selected
            elif 'gas_station_owner' in request.POST:
                GasStationOwner.objects.create(user=user)
                messages.success(request, 'Account created as a gas station owner.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

  # login page
def user_login(request):
      if request.method == 'POST':
          form = LoginForm(request.POST)
          if form.is_valid():
              username = request.POST.get('username')
              password = request.POST.get('password')

              user = authenticate(request, username=username, password=password)

              if not user:
                  # Authentication failed, handle accordingly
                  messages.error(request, "Invalid username or password.")
                  print("Authentication failed.")
              else:
                  # User is authenticated, log in
                  login(request, user)

                  # Check if the user is a customer or gas station owner
                  try:
                      customer = Customer.objects.get(user=user)
                      # User is a customer, redirect to index.html (replace with the actual customer page)
                      print("User is a customer. Redirecting to index.html.")
                      return redirect('index')  # Replace 'index' with the actual customer page name
                  except Customer.DoesNotExist:
                      pass

                  try:
                      station_owner = GasStationOwner.objects.get(user=user)
                      # User is a gas station owner, redirect to stationowner.html
                      print("User is a gas station owner. Redirecting to stationowner.html.")
                      return redirect('stationowner')
                  except GasStationOwner.DoesNotExist:
                      pass

                  # User is not a customer or gas station owner, handle accordingly
                  print("User is not a customer or gas station owner.")
                  return redirect('index')

      else:
          # If the request method is not POST, render the login form
          form = LoginForm()

      # Rendering the login form
      return render(request, 'login.html', {'user': request.user, 'form': form})


  # To Return HttpResponse always
  #  return HttpResponse("An error occurred in the login process.")

# logout page
def user_logout(request):
    logout(request)
    return redirect('index')


def update_gas_prices(request):
  if request.method == 'POST':
    form = GasPriceUpdateForm(request.POST)
    if form.is_valid():
        form.save()
  Gas_Price_Update_Form = GasPriceUpdateForm()
  return render(request, 'update_gas_prices.html', {"Gas_Price_Update_Form": Gas_Price_Update_Form})


def render_feedback_form(request):
  if request.method == 'POST':
    form = FeedbackForm(request.POST)
    if form.is_valid():
      feedback_instance = form.save() # Saving the form data to the database
      messages.success(request, "Your feedback has been submitted!")
      # return redirect('feedback')
      #return render(request, 'display_feedback.html', {'form': form}) # Redirect to a new URL to display the form data:
      return redirect('feedback_success', id=feedback_instance.id)  # Redirect to another view that can display the submitted data or send an email, etc.
  else: 
    form = FeedbackForm()
  #return render(request, 'feedback.html', {'form': form})
   # Fetch all feedback entries to display below the form
    feedback_entries = Feedback.objects.all()
    return render(request, 'feedback.html', {'form': form, 'feedback_entries': feedback_entries})

def feedback_success(request, id=None):
    if id:
        feedback_entries = Feedback.objects.filter(id=id)
    else:
        feedback_entries = Feedback.objects.all()
    return render(request, 'feedback_success.html', {'feedback_entries': feedback_entries})

def delete_feedback(request, id):
    if request.user.is_staff:
        feedback = get_object_or_404(Feedback, id=id)
        feedback.delete()
        return HttpResponseRedirect(reverse('feedback_success'))
        #return render(request, 'feedback_success.html', {'feedback_entries': feedback_entries})
    else:
        return HttpResponse("Unauthorized", status=401)
    
def all_feedback_success(request):
    feedback_entries = Feedback.objects.all()
    return render(request, 'feedback_success.html', {'feedback_entries': feedback_entries})


    feedback = get_object_or_404(Feedback, id=id)
    feedback.delete()
    return HttpResponseRedirect(reverse('feedback_success'))

def map_view(request):

    geolocator = Nominatim(timeout=10, user_agent="Fuel Buddy")
    location = 'Colorado'

    stations =  Gas_Station.objects.all()

    location = "Colorado springs" # For testing, doesn't need structure so it can be any address string. zipcodes seem to be the most accurate though.

    locator = geolocator.geocode(location) # converts addresses to coordinates
    if location == 'Colorado':
        station_map = folium.Map(location=[locator.latitude, locator.longitude], zoom_start=8)
    else:
        station_map = folium.Map(location=[locator.latitude, locator.longitude], zoom_start=13)


    folium.Marker([locator.latitude, locator.longitude]).add_to(station_map)
    folium.Circle([locator.latitude, locator.longitude], radius=16090/2).add_to(station_map) # distance is in meters, multiply by 1609 for conversion to miles. 

    for station in stations:
        coords = (station.latitude, station.longitude)
        folium.Marker(coords).add_to(station_map)

    context = {'map': station_map._repr_html_()}

    return render(request, 'station-tracker.html', context)

def user_about(request):
   return render(request, 'about.html')

def user_fueldemand(request):
   return render(request, 'fueldemand.html')

def user_stationowner(request):
   return render(request, 'stationowner.html')

def user_payment(request):
   return render(request, 'payment.html')




