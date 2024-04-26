from django.db import models

class Search(models.Model):
    location = models.CharField(max_length = 100)
    range = models.CharField(max_length = 100)
    fuelType = models.CharField(max_length = 100, null = True)
    searchPref = models.CharField(max_length = 100, null = True)

    def __str__(self):
        return f"{self.location}"