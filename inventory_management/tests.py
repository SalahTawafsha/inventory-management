from django.db import IntegrityError
from django.test import TestCase

from inventory_management.models import Product, Location, ProductMovement


class ProductModelTests(TestCase):
    """ Testing for Product model. """

    def test_create_duplicated_product(self):
        """ test create duplicated product. """
        Product.objects.create(product_id="Apple")

        self.assertRaises(IntegrityError, lambda: Product.objects.create(product_id="Apple"))


class LocationModelTests(TestCase):
    """ Testing for Location model. """

    def test_create_duplicated_product(self):
        """ test create duplicated Location. """
        Location.objects.create(location_id="Ramallah")

        self.assertRaises(IntegrityError, lambda: Location.objects.create(location_id="Ramallah"))


class ProductMovementModelTests(TestCase):
    """ Testing for ProductMovement model. """

    def test_create_with_blank_from_location(self):
        """ test create with blank from_location. """
        product, location = createProductAndLocation("Apple", "Ramallah")

        product_movement = ProductMovement.objects.create(product_id=product, to_location=location, quantity=12)

        self.assertAllFields(product_movement, product, None, location, 12)

    def test_create_with_blank_to_location(self):
        """ test create with blank to_location. """
        product, location = createProductAndLocation("Apple", "Ramallah")

        ProductMovement.objects.create(product_id=product, to_location=location, quantity=12)
        product_movement = ProductMovement.objects.create(product_id=product, from_location=location, quantity=12)

        self.assertAllFields(product_movement, product, location, None, 12)

    def test_create_with_both_blank_locations(self):
        """ test create with both blank locations. """
        product = Product.objects.create(product_id="Apple")

        self.assertRaisesRegex(IntegrityError, "Both 'from location' and 'to location' can't be blank.",
                               lambda: ProductMovement.objects.create(product_id=product, quantity=12), )

    def test_fill_both_locations(self):
        """ test move from a location to other location """

        product, first_location, second_location \
            = createProductAndLocations("Apple", "Ramallah", "Nablus")

        ProductMovement.objects.create(product_id=product,
                                       to_location=first_location, quantity=12)

        product_movement = ProductMovement.objects.create(product_id=product, from_location=first_location,
                                                          to_location=second_location, quantity=12)

        self.assertAllFields(product_movement, product, first_location, second_location, 12)

    def test_move_to_same_location(self):
        product, location = createProductAndLocation("Apple", "Ramallah")

        self.assertRaisesRegex(IntegrityError,
                               "Can't move from location to same location.",
                               lambda: ProductMovement.objects.create(product_id=product, from_location=location,
                                                                      to_location=location,
                                                                      quantity=6), )

    def test_move_quantity_not_enough_quantity(self):
        """ test move with not enough quantity."""

        product, first_location, second_location \
            = createProductAndLocations("Apple", "Ramallah", "Nablus")

        ProductMovement.objects.create(product_id=product, from_location=None, to_location=first_location, quantity=5)

        self.assertRaisesRegex(IntegrityError,
                               "Product balance in Ramallah is 5 so, can't move 6 from it",
                               lambda: ProductMovement.objects.create(product_id=product, from_location=first_location,
                                                                      to_location=second_location,
                                                                      quantity=6), )

    def test_move_to_two_locations_with_not_enough_for_second(self):
        """ test create with not enough quantity."""

        product, first_location, second_location \
            = createProductAndLocations("Apple", "Ramallah", "Nablus")

        third_location = Location.objects.create(location_id="Jenin")

        ProductMovement.objects.create(product_id=product, from_location=None, to_location=first_location, quantity=12)

        ProductMovement.objects.create(product_id=product, from_location=first_location,
                                       to_location=second_location, quantity=5)

        self.assertRaisesRegex(IntegrityError,
                               "Product balance in Ramallah is 7 so, can't move 8 from it",
                               lambda: ProductMovement.objects.create(product_id=product, from_location=first_location,
                                                                      to_location=third_location,
                                                                      quantity=8), )

    def test_update_quantity_more_than_exist(self):
        """ test update with not enough quantity."""

        product, first_location, second_location \
            = createProductAndLocations("Apple", "Ramallah", "Nablus")

        ProductMovement.objects.create(product_id=product, from_location=None, to_location=first_location, quantity=5)

        product_movement = ProductMovement.objects.create(product_id=product, from_location=first_location,
                                                          to_location=second_location,
                                                          quantity=3)
        product_movement.quantity = 6
        self.assertRaisesRegex(IntegrityError,
                               "Product balance in Ramallah is 5 so, can't move 6 from it",
                               lambda: product_movement.save(), )

    def assertAllFields(self, product_movement, product, from_location, to_location, quantity):
        """ validate all fields of product_movement """
        self.assertEquals(product_movement.product_id, product)
        self.assertEquals(product_movement.from_location, from_location)
        self.assertEquals(product_movement.to_location, to_location)
        self.assertEquals(product_movement.quantity, quantity)


def createProductAndLocation(product_id: str, location_id: str):
    """ create product and location to use in testing """

    product = Product.objects.create(product_id=product_id)
    location = Location.objects.create(location_id=location_id)

    return product, location


def createProductAndLocations(product_id: str, first_location_id: str, second_location_id: str):
    """ create product and locations to use in testing """

    product, first_location = createProductAndLocation(product_id, first_location_id)
    second_location = Location.objects.create(location_id=second_location_id)

    return product, first_location, second_location
