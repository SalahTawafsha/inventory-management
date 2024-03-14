from django.contrib import admin

from inventory_management.models import Product, Location, ProductMovement


# Register your models here.

class ProductMovementAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "product_id", "from_location", "to_location", "quantity")


class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_id"]


class LocationAdmin(admin.ModelAdmin):
    list_display = ["location_id"]


admin.site.register(Product, ProductAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(ProductMovement, ProductMovementAdmin)
