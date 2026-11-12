from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('product-view/',views.product_view,name="product_view"),
    path('product-create/',views.product_create,name="product_create"),
    path('product-edit/<int:pk>/',views.product_edit,name="product_edit"),
    path('product-delete/<int:pk>/',views.product_delete,name="product_delete"),
]
