from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('create-reservation/', views.create_reservation, name='create-reservation'),
    path('create-order/', views.create_order, name='create-order'),
    path('<uuid:order_id>/cancel/', views.cancel_order, name='cancel-order'),
]
