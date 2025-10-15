from django import forms
from .models import Pesticide

class PesticideForm(forms.ModelForm):
    class Meta:
        model = Pesticide
        fields = ['pesticide_name', 'price', 'quantity_available']  # Include stock and price fields
