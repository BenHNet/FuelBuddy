from django import forms
from .models import Search


class SearchForm(forms.ModelForm):
   
    class Meta:
        model = Search
        fields = ['location','range','fuelType',
        'searchPref']
        #fields = ['location',]
