from django import forms
from django.forms.utils import ErrorList

from inventory_management.models import Location, Product


class ProductForm(forms.Form):
    product_id = forms.CharField(label="Product ID", required=True, max_length=50,
                                 widget=forms.TextInput(attrs={'class': 'did-floating-input'}))


class LocationForm(forms.Form):
    location_id = forms.CharField(label="Location ID", required=True, max_length=50,
                                  widget=forms.TextInput(attrs={'class': 'did-floating-input'}))


class ProductMovementForm(forms.Form):
    PRODUCTS = Product.get_products()
    LOCATIONS = Location.get_locations()

    product_id = forms.ChoiceField(label="Product ID", required=True,
                                   widget=forms.Select(attrs={'class': 'did-floating-select'}),
                                   choices=PRODUCTS)

    from_location = forms.ChoiceField(label="From Location", required=False,
                                      widget=forms.Select(
                                          attrs={'class': 'did-floating-select', "id": "form_location"}),
                                      choices=LOCATIONS)
    to_location = forms.ChoiceField(label="To Location", required=False,
                                    widget=forms.Select(attrs={'class': 'did-floating-select', "id": "to_location"}),
                                    choices=LOCATIONS)

    quantity = forms.CharField(label="Quantity", required=True,
                               widget=forms.TextInput(
                                   attrs={'class': 'did-floating-input', 'type': 'number', 'value': "1", "min": 1}))
