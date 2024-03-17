from django import forms

from inventory_management.models import Location, Product


class ProductForm(forms.Form):
    product_id = forms.CharField(label="Product ID", required=True, max_length=50,
                                 widget=forms.TextInput(attrs={'class': 'did-floating-input'}))


class LocationForm(forms.Form):
    location_id = forms.CharField(label="Location ID", required=True, max_length=50,
                                  widget=forms.TextInput(attrs={'class': 'did-floating-input'}))


class ProductMovementForm(forms.Form):
    product_id = forms.ChoiceField(label="Product ID", required=True,
                                   widget=forms.Select(attrs={'class': 'did-floating-select'}), )

    from_location = forms.ChoiceField(label="From Location", required=False,
                                      widget=forms.Select(
                                          attrs={'class': 'did-floating-select', "id": "form_location"}), )
    to_location = forms.ChoiceField(label="To Location", required=False,
                                    widget=forms.Select(attrs={'class': 'did-floating-select', "id": "to_location"}), )

    quantity = forms.CharField(label="Quantity", required=True,
                               widget=forms.TextInput(
                                   attrs={'class': 'did-floating-input', 'type': 'number', 'value': "1", "min": 1}))

    def __init__(self, *args, **kwargs):
        products = Product.get_products()
        locations = Location.get_locations()

        super(ProductMovementForm, self).__init__(*args, **kwargs)

        self.fields['product_id'].choices = products

        self.fields['from_location'].choices = locations

        self.fields['to_location'].choices = locations
