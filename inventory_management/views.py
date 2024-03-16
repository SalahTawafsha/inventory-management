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
    if location_id == "":
        return None

    return get_object_or_404(Location, location_id=location_id)


def index(request):
    products_balance = ProductMovement.get_product_balance_in_locations()
    return render(request, "dashboard/index.html", {"products_balance": products_balance})


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

    products_list = Product.objects.all().order_by("product_id")
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

    locations_list = Location.objects.all().order_by("location_id")
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


def addProductMovement(request, form):
    product = get_object_or_404(Product, product_id=form.cleaned_data["product_id"])
    from_location = get_location(form.cleaned_data["from_location"])
    to_location = get_location(form.cleaned_data["to_location"])

    ProductMovement.objects.create(product_id=product,
                                   from_location=from_location,
                                   to_location=to_location,
                                   quantity=form.cleaned_data["quantity"])


def product_movement(request):
    if request.method == "POST":
        form = ProductMovementForm(request.POST)
        if form.is_valid():
            try:
                addProductMovement(request, form)
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
    movement = get_object_or_404(ProductMovement, movement_id=product_movement_id)
    if request.method == "POST":
        try:
            movement.quantity = request.POST["quantity"]
            movement.save()

        except IntegrityError as e:
            messages.error(request, str(e))

    return HttpResponseRedirect(reverse("product_movement"))
