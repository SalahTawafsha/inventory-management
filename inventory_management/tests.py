from django.db import IntegrityError
from django.test import TestCase

from inventory_management.models import Product, Location, ProductMovement


class ProductModelTests(TestCase):
    """ Testing for Product model. """

    def test_create_duplicated_product(self):
        """ test create duplicated product."""
        Product.objects.create(product_id="Apple")

        self.assertRaises(IntegrityError, lambda: Product.objects.create(product_id="Apple"))


class LocationModelTests(TestCase):
    """ Testing for Location model. """

    def test_create_duplicated_product(self):
        """ test create duplicated Location."""
        Location.objects.create(location_id="Ramallah")

        self.assertRaises(IntegrityError, lambda: Location.objects.create(location_id="Ramallah"))


def createProductAndLocations(product_id: str, first_location_id: str, second_location_id: str):
    product, first_location = createProductAndLocation(product_id, first_location_id)
    second_location = Location.objects.create(location_id=second_location_id)

    return product, first_location, second_location


class ProductMovementModelTests(TestCase):
    """ Testing for ProductMovement model. """

    def test_create_with_blank_from_location(self):
        """ test create with blank from_location."""
        product, location = createProductAndLocation("Apple", "Ramallah")

        product_movement = ProductMovement.objects.create(product_id=product, to_location=location, quantity=12)

        self.assertAllFields(product_movement, product, None, location, 12)

    def test_create_with_blank_to_location(self):
        """ test create with blank to_location."""
        product, location = createProductAndLocation("Apple", "Ramallah")

        product_movement = ProductMovement.objects.create(product_id=product, from_location=location, quantity=12)

        self.assertAllFields(product_movement, product, location, None, 12)

    def test_fill_both_locations(self):
        product, first_location, second_location \
            = createProductAndLocations("Apple", "Ramallah", "Nablus")

        product_movement = ProductMovement.objects.create(product_id=product, from_location=first_location,
                                                          to_location=second_location, quantity=12)

        self.assertAllFields(product_movement, product, first_location, second_location, 12)

    def test_create_with_both_blank_locations(self):
        """ test create with both blank locations."""
        product = Product.objects.create(product_id="Apple")

        self.assertRaisesRegex(Exception, "Both 'from location' and 'to location' can't be blank.",
                               lambda: ProductMovement.objects.create(product_id=product, quantity=12), )

    def assertAllFields(self, product_movement, product, from_location, to_location, quantity):
        self.assertEquals(product_movement.product_id, product)
        self.assertEquals(product_movement.from_location, from_location)
        self.assertEquals(product_movement.to_location, to_location)
        self.assertEquals(product_movement.quantity, quantity)


def createProductAndLocation(product_id: str, location_id: str):
    product = Product.objects.create(product_id=product_id)
    location = Location.objects.create(location_id=location_id)

    return product, location
