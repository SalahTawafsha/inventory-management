from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404

from inventory_management.forms import ProductForm, LocationForm
from inventory_management.models import Product, Location


# Create your views here.
def index(request):
    return render(request, "dashboard/index.html")


def products(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                Product.objects.create(product_id=form.cleaned_data["product_id"])
            except IntegrityError:
                messages.error(request,
                               "This Product is already exist")
        else:
            messages.error(request,
                           "Invalid Form")

    products_list = Product.objects.values()
    return render(request, "products/product.html", {'form': ProductForm(), "products_list": products_list})


def locations(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            try:
                Location.objects.create(location_id=form.cleaned_data["location_id"])
            except IntegrityError:
                messages.error(request,
                               "This Location is already exist")
        else:
            messages.error(request,
                           "Invalid Form")

    locations_list = Location.objects.values()
    return render(request, "locations/location.html", {'form': LocationForm(), "locations_list": locations_list})


def edit_product(request, product_id: str):
    product = get_object_or_404(Product, product_id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid() and form.cleaned_data["product_id"] != product_id:
            Product.objects.filter(product_id=product_id).update(product_id=form.cleaned_data["product_id"])

    return render(request, "products/edit_product.html",
                  {"product": product, "form": ProductForm(initial={"product_id": product.product_id})})
