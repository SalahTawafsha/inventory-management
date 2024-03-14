from django.db import models
from django.utils import timezone


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
            raise Exception("Both 'from location' and 'to location' can't be blank.")

        super().save(*args, **kwargs)
