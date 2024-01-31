from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Customer(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  # Add any additional fields for the Customer model

class GasStationOwner(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  # Add any additional fields for the GasStationOwner model

class Gas_Station(models.Model):
  station_name = models.CharField(max_length=200)
  address = models.CharField(max_length=100, default='UCCS')
  latitude = models.FloatField()
  longitude = models.FloatField()
  regular_gas_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
  premium_gas_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
  diesel_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

  def __str__(self):
    return self.station_name

class Feedback(models.Model):
  name = models.CharField(max_length=50)
  email = models.EmailField()
  phone = models.IntegerField()
  comments = models.TextField()
  gasStationAddr = models.CharField(max_length=200)

  def __str__(self):
    return self.name


        # Model for the About Us page
class AboutUs(models.Model):
        # Fields for the About Us page
        title = models.CharField(max_length=200)
        content = models.TextField()
        image = models.ImageField(upload_to='about_us_images/')
        # Add any other fields you need for the About Us page

#!/usr/bin/env python3