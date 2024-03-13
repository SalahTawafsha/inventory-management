from django import forms


class ProductForm(forms.Form):
    product_id = forms.CharField(label="Product ID", required=True, max_length=50,
                                 widget=forms.TextInput(attrs={'class': 'did-floating-input'}))


class LocationForm(forms.Form):
    location_id = forms.CharField(label="Location ID", required=True, max_length=50,
                                  widget=forms.TextInput(attrs={'class': 'did-floating-input'}))
