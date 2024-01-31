from django.db import models



class Search(models.Model):
    location = models.CharField(max_length = 100)
    range = models.CharField(max_length = 100)
    fuelType = models.CharField(max_length = 100, null = True)
    searchPref = models.CharField(max_length = 100, null = True)

    def __str__(self):
        return f"{self.location}"


# class Gas_Station(models.Model):
#   station_name = models.CharField(max_length=200)
#   latitude = models.FloatField()
#   longitude = models.FloatField()
#   regular_gas_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
#   premium_gas_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
#   diesel_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

#   def __str__(self):
#     return self.station_name



