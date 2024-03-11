from django.contrib import admin

from inventory_management.models import Product, Location, ProductMovement

# Register your models here.

admin.site.register(Product)
admin.site.register(Location)
admin.site.register(ProductMovement)
