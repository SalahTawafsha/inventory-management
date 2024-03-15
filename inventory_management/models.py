from django.db import models, connection, IntegrityError
from django.utils import timezone

GET_PRODUCTS_BALANCE_QUERY = """
SELECT to_location_table.product_id_id,
       to_location_table.to_location_id,
       (to_location_table.sum_quantity - COALESCE(from_location_table.sum_quantity, 0)) AS net_quantity
FROM (SELECT product_id_id,
             to_location_id,
             SUM(quantity) AS sum_quantity
      FROM inventory_management_productmovement
      GROUP BY product_id_id, to_location_id) AS to_location_table
         LEFT JOIN (SELECT product_id_id,
                           from_location_id,
                           SUM(quantity) AS sum_quantity
                    FROM inventory_management_productmovement
                    WHERE from_location_id IS NOT NULL
                    GROUP BY product_id_id, from_location_id) AS from_location_table
                   ON to_location_table.to_location_id = from_location_table.from_location_id AND
                      to_location_table.product_id_id = from_location_table.product_id_id;
"""

GET_PRODUCT_BALANCE_IN_LOCATION_QUERY = """
SELECT
    COALESCE(SUM(CASE WHEN to_location_id = '{location_id}' THEN quantity ELSE -quantity END), 0)
from inventory_management_productmovement
where product_id_id = '{product_id}' and (from_location_id = '{location_id}' or to_location_id = '{location_id}');
"""


# Create your models here.

class Product(models.Model):
    product_id = models.CharField("Product", primary_key=True, max_length=50)

    @staticmethod
    def get_products():
        choices = []
        for product in Product.objects.all().order_by("product_id"):
            choices.append((product.product_id, product.product_id))

        return tuple(choices)

    def __str__(self):
        return self.product_id


class Location(models.Model):
    location_id = models.CharField("Location", primary_key=True, max_length=50)

    @staticmethod
    def get_locations():
        choices = [("", "")]
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
        if not self.from_location and not self.to_location:
            raise IntegrityError("Both 'from location' and 'to location' can't be blank.")

        if self.from_location:
            balance_of_product_in_location = (
                ProductMovement.get_balance_of_product_in_location(str(self.product_id),
                                                                   str(self.from_location)))
            if balance_of_product_in_location < int(self.quantity):
                raise IntegrityError(
                    f"Product balance in {self.from_location} is {balance_of_product_in_location} "
                    f"so, can't move {self.quantity} from it")

        super().save(*args, **kwargs)

    @staticmethod
    def get_product_balance_in_locations():
        cursor = connection.cursor()
        cursor.execute(GET_PRODUCTS_BALANCE_QUERY)
        results = cursor.fetchall()

        return results

    @staticmethod
    def get_balance_of_product_in_location(product_id: str, location_id: str):
        if not isinstance(product_id, str) or not isinstance(location_id, str):
            raise TypeError()

        cursor = connection.cursor()
        cursor.execute(GET_PRODUCT_BALANCE_IN_LOCATION_QUERY.format(location_id=location_id, product_id=product_id))
        results = cursor.fetchall()

        return int(results[0][0])
