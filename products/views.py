# products/views.py - REMOVE AUTHENTICATION REQUIREMENT
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny  # ✅ Import this
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # ✅ CHANGE FROM IsAuthenticated TO AllowAny
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True)

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # ✅ CHANGE THIS TOO
    queryset = Product.objects.filter(is_active=True)

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # ✅ CHANGE THIS TOO
    queryset = Category.objects.filter(is_active=True)
