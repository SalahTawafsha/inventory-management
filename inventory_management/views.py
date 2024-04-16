from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Case, When, Value
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from inventory_management.forms import ProductForm, LocationForm, ProductMovementForm
from inventory_management.models import Product, Location, ProductMovement


# Create your views here.
def get_location(location_id):
    """ get location_id from database """
    if location_id == "":
        return None

    return get_object_or_404(Location, location_id=location_id)


def index(request):
    """ dashboard render """

    products_balance = ProductMovement.get_quantity_of_all_products_in_location()
    return render(request, "dashboard/index.html", {"products_balance": products_balance})


def update(request):
    products_balance = ProductMovement.get_quantity_of_all_locations_products_counts()
    products_list = Product.objects.all().order_by("product_id")
    locations_list = Location.objects.all().order_by("location_id")

    return render(request, "dashboard/update.html",
                  {"products_balance": products_balance, "products_list": products_list,
                   "locations_list": locations_list})


def products(request):
    """ products view that has form of add product """

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

    products_list = Product.objects.all().order_by("product_id")
    return render(request, "products/product.html", {'form': ProductForm(), "products_list": products_list})


def edit_product(request, product_id: str):
    """ edit product that work on POST request """

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


def locations(request):
    """ locations view that has form of add location """

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

    locations_list = Location.objects.all().order_by("location_id")
    return render(request, "locations/location.html", {'form': LocationForm(), "locations_list": locations_list})


def edit_location(request, location_id: str):
    """ edit location that work on POST request """

    location = get_object_or_404(Location, location_id=location_id)
    if request.method == "POST":
        if request.POST["location_id"] != location_id:
            try:
                # create new location, update all foreign keys to new value and delete old one
                new_location = Location.objects.create(location_id=request.POST["location_id"])
                ProductMovement.objects.update(
                    from_location_id=Case(
                        When(from_location_id=location_id, then=Value(new_location.location_id)),
                    ),
                    to_location_id=Case(
                        When(to_location_id=location_id, then=Value(new_location.location_id)),
                    ),
                )

                location.delete()

            except IntegrityError:
                messages.error(request,
                               "This Location is already exist")

    return HttpResponseRedirect(reverse("locations"))


def product_movement(request):
    """ ProductMovement view that has form of add ProductMovement """

    if request.method == "POST":
        form = ProductMovementForm(request.POST)
        if form.is_valid():
            try:
                product = get_object_or_404(Product, product_id=form.cleaned_data["product_id"])
                from_location = get_location(form.cleaned_data["from_location"])
                to_location = get_location(form.cleaned_data["to_location"])

                ProductMovement.objects.create(product_id=product,
                                               from_location=from_location,
                                               to_location=to_location,
                                               quantity=form.cleaned_data["quantity"])

            except IntegrityError as e:
                messages.error(request, str(e))
            finally:
                # this redirect is to avoid render with POST method
                # since if render with POST will make problem that will add again if refresh page
                return HttpResponseRedirect(reverse("product_movement"))
        else:
            messages.error(request,
                           form.errors)

    form = ProductMovementForm()
    product_movements = ProductMovement.objects.all().order_by("product_id", "from_location", "to_location")
    return render(request, "product_movement/product_movement.html",
                  {"form": form, "product_movements": product_movements})


def edit_product_movement(request, product_movement_id: str):
    """ edit ProductMovement that work on POST request """

    movement = get_object_or_404(ProductMovement, movement_id=product_movement_id)
    if request.method == "POST":
        try:
            movement.quantity = request.POST["quantity"]
            movement.save()

        except IntegrityError as e:
            messages.error(request, str(e))

    return HttpResponseRedirect(reverse("product_movement"))
