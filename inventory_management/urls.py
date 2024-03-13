from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('products/', views.products, name="products"),
    path('products/<str:product_id>', views.edit_product, name="edit_product"),
    path('locations/', views.locations, name="locations"),
]
