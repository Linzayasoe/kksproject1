from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('receipt-create/',views.receipt_create,name="receipt_create"),
    path('receipt-detail/<int:pk>/',views.receipt_detail,name="receipt_detail"),
    path('receipt-view/',views.receipt_view,name="receipt_view"),
]
