from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('update', views.update, name="update"),
    path('products/', views.products, name="products"),
    path('products/<str:product_id>', views.edit_product, name="edit_product"),
    path('locations/', views.locations, name="locations"),
    path('locations/<str:location_id>', views.edit_location, name="edit_location"),
    path('product-movement/', views.product_movement, name="product_movement"),
    path('product-movement/<str:product_movement_id>', views.edit_product_movement, name="edit_product_movement"),
]
