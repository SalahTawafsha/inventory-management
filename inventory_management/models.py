from django.db import models, IntegrityError
from django.utils import timezone


# Create your models here.

class Product(models.Model):
    product_id = models.CharField("Product", primary_key=True, max_length=50)

    @staticmethod
    def get_products():
        """ Get all products as list of tuple to used for combobox of product in ProductMovement Form """
        choices = []
        # get products ordered by product_id for better user experience
        for product in Product.objects.all().order_by("product_id"):
            choices.append((product.product_id, product.product_id))

        return tuple(choices)

    def __str__(self):
        return self.product_id


class Location(models.Model):
    location_id = models.CharField("Location", primary_key=True, max_length=50)

    @staticmethod
    def get_locations():
        """ Get all locations as list of tuple to used for combo boxes of locations in ProductMovement Form """

        # first choice is empty to used for blank location (move into location and move out cases)
        choices = [("", "")]
        # get locations ordered by product_id for better user experience
        for location in Location.objects.all().order_by("location_id"):
            choices.append((location.location_id, location.location_id))

        return tuple(choices)

    def __str__(self):
        return self.location_id


class ProductMovement(models.Model):
    movement_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField("Time of Move", default=timezone.now)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    from_location = models.ForeignKey(Location, related_name="from_location", on_delete=models.CASCADE, null=True,
                                      default=None)
    to_location = models.ForeignKey(Location, related_name="to_location", on_delete=models.CASCADE, null=True,
                                    default=None)
    quantity = models.IntegerField("Moved Quantity")

    def save(self, *args, **kwargs):
        """ override save function to add input validation """

        # check if both locations are nor provided
        if not self.from_location and not self.to_location:
            raise IntegrityError("Both 'from location' and 'to location' can't be blank.")

        # check if same from and to location
        if self.from_location == self.to_location:
            raise IntegrityError("Can't move from location to same location.")

        # check if there is enough available quantity in location that we want to move products from it
        if self.from_location:
            balance_of_product_in_location = (
                ProductMovement.get_quantity_of_product_in_location(str(self.product_id),
                                                                    str(self.from_location),
                                                                    str(self.movement_id)))
            if balance_of_product_in_location < int(self.quantity):
                raise IntegrityError(
                    f"Product balance in {self.from_location} is {balance_of_product_in_location} "
                    f"so, can't move {self.quantity} from it")

        super().save(*args, **kwargs)

    @staticmethod
    def get_quantity_of_all_products_in_location() -> dict:
        """ method that returns dict of products and quantity in each location """

        # dictionary that will have format:
        # {'product': {'location_1': count_location_1, 'location_2': count_location_2}}
        results = {}

        # loop on all movements with -quantity when move from location and with +quantity when move to location
        for product_movement in ProductMovement.objects.all():
            product_id = product_movement.product_id.product_id

            from_location, to_location = get_from_and_to_locations(product_movement)
            quantity = product_movement.quantity

            if from_location is not None:
                add_location_quantity(results, product_id, from_location, -quantity)

            add_location_quantity(results, product_id, to_location, quantity)

        return results

    @staticmethod
    def get_quantity_of_product_in_location(product_id: str, location_id: str, movement_id: str):
        """ get how much net quantity of a product in a location """

        if not isinstance(product_id, str) or not isinstance(location_id, str) or not isinstance(movement_id, str):
            raise TypeError()

        count = 0

        # loop on all movements and add or subtract quantity when have same product_id and location_id
        for product_movement in ProductMovement.objects.all():
            current_product_id = product_movement.product_id.product_id
            if product_id == current_product_id and str(product_movement.movement_id) != movement_id:
                from_location, to_location = get_from_and_to_locations(product_movement)

                quantity = product_movement.quantity

                if from_location == location_id:
                    count = count - quantity

                if to_location == location_id:
                    count = count + quantity

        return count


def add_location_quantity(results, product_id, location, quantity):
    """ method that add quantity of product to count of quantity in a location """

    location = "None" if type(location) is None else location
    if product_id in results.keys():
        if location in results[product_id].keys():
            results[product_id][location] = results[product_id][location] + quantity
        else:
            results[product_id][location] = quantity
    else:
        results.update({product_id: {location: quantity}})


def get_from_and_to_locations(product_movement):
    """ get location_id for 'from_location' and 'to_location' a product_movement object """

    from_location = product_movement.from_location.location_id \
        if product_movement.from_location is not None else None

    to_location = product_movement.to_location.location_id \
        if product_movement.to_location is not None else "None"

    return from_location, to_location
