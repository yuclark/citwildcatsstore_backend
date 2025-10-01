# orders/views.py - REMOVE AUTHENTICATION FOR TESTING
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # ✅ Import this
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateReservationSerializer
from products.models import Product

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]  # ✅ CHANGE FROM IsAuthenticated
    
    def get_queryset(self):
        # For testing, show all orders - later filter by user
        return Order.objects.all()

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]  # ✅ CHANGE THIS TOO
    
    def get_queryset(self):
        return Order.objects.all()

@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ CHANGE FROM IsAuthenticated
def create_reservation(request):
    serializer = CreateReservationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                product_id = serializer.validated_data['product_id']
                quantity = serializer.validated_data['quantity']
                notes = serializer.validated_data.get('notes', '')
                
                # Get the product
                product = Product.objects.get(id=product_id, is_active=True)
                
                # Check if enough stock
                if product.stock_quantity < quantity:
                    return Response({
                        'error': f'Insufficient stock. Only {product.stock_quantity} available.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # ✅ FOR TESTING - Create fake user or use admin user
                from authentication.models import CustomUser
                user = CustomUser.objects.filter(is_superuser=True).first()
                if not user:
                    return Response({'error': 'No admin user found'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Create the reservation/order
                order = Order.objects.create(
                    user=user,  # ✅ Use admin user for testing
                    order_type='reservation',
                    status='pending',
                    notes=notes,
                    total_amount=0
                )
                
                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )
                
                # Update order total
                order.total_amount = order_item.total_price
                order.save()
                
                # Return the created order
                response_serializer = OrderSerializer(order)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found or inactive.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ CHANGE THIS TOO
def create_order(request):
    # Same logic as create_reservation but with order_type='order'
    serializer = CreateReservationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                product_id = serializer.validated_data['product_id']
                quantity = serializer.validated_data['quantity']
                notes = serializer.validated_data.get('notes', '')
                
                product = Product.objects.get(id=product_id, is_active=True)
                
                if product.stock_quantity < quantity:
                    return Response({
                        'error': f'Insufficient stock. Only {product.stock_quantity} available.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Use admin user for testing
                from authentication.models import CustomUser
                user = CustomUser.objects.filter(is_superuser=True).first()
                if not user:
                    return Response({'error': 'No admin user found'}, status=status.HTTP_400_BAD_REQUEST)
                
                order = Order.objects.create(
                    user=user,
                    order_type='order',
                    status='pending',
                    notes=notes,
                    total_amount=0
                )
                
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=product.price
                )
                
                order.total_amount = order_item.total_price
                order.save()
                
                # Reduce stock for orders
                product.stock_quantity -= quantity
                product.save()
                
                response_serializer = OrderSerializer(order)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([AllowAny])  # ✅ CHANGE THIS TOO
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        
        if order.status in ['released', 'cancelled']:
            return Response({
                'error': f'Cannot cancel order with status: {order.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'cancelled'
        order.save()
        
        if order.order_type == 'order':
            for item in order.items.all():
                item.product.stock_quantity += item.quantity
                item.product.save()
        
        response_serializer = OrderSerializer(order)
        return Response(response_serializer.data)
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
