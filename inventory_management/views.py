from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from inventory_management.forms import ProductForm, LocationForm
from inventory_management.models import Product, Location, ProductMovement


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
        if request.POST["product_id"] != product_id:
            try:
                new_product = Product.objects.create(product_id=request.POST["product_id"])
                ProductMovement.objects.filter(product_id=product_id).update(product_id=new_product.product_id)
                product.delete()

            except IntegrityError:
                messages.error(request,
                               "This product is already exist")

    return HttpResponseRedirect(reverse("products"))


def edit_location(request, location_id: str):
    location = get_object_or_404(Location, location_id=location_id)
    if request.method == "POST":
        if request.POST["location_id"] != location_id:
            try:
                new_location = Location.objects.create(location_id=request.POST["location_id"])
                ProductMovement.objects \
                    .filter(to_location=location_id).update(to_location=new_location.location_id)
                ProductMovement.objects \
                    .filter(from_location=location_id).update(from_location=new_location.location_id)

                location.delete()

            except IntegrityError:
                messages.error(request,
                               "This Location is already exist")

    return HttpResponseRedirect(reverse("locations"))
