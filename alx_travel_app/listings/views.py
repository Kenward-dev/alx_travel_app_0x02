from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
import requests
from .models import Listing, Booking, Review, Payment
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer


class ListingListView(generics.ListCreateAPIView):
    """
    List all listings or create a new listing
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific listing
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BookingCreateView(generics.CreateAPIView):
    """
    Create a new booking
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Automatically set the user to the current user
        serializer.save(user=self.request.user)


class BookingListView(generics.ListAPIView):
    """
    List bookings for the current user
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class BookingDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific booking
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    List all reviews or create a new review
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        # Automatically set the user to the current user
        serializer.save(user=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific review
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class InitiatePaymentView(APIView):
    """
    Initiate payment with Chapa
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Get booking data from request
            booking_id = request.data.get('booking_id')
            amount = request.data.get('amount')
            
            if not booking_id or not amount:
                return Response({
                    'error': 'booking_id and amount are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get the booking
            try:
                booking = Booking.objects.get(id=booking_id, user=request.user)
            except Booking.DoesNotExist:
                return Response({
                    'error': 'Booking not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Create payment object and save it to get an ID
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                status='pending'
            )
            
            # Generate transaction reference
            tx_ref = payment.generate_tx_ref()
            
            # Prepare payload for Chapa
            payload = {
                'amount': str(amount),
                'currency': 'ETB',
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone_number': request.data.get('phone_number', ''),
                'tx_ref': tx_ref,
                'callback_url': request.data.get('callback_url', ''),
                'return_url': request.data.get('return_url', ''),
                'customization': {
                    'title': f'Payment for {booking.listing.title}',
                    'description': f'Booking payment from {booking.start_date} to {booking.end_date}'
                }
            }
            
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.chapa.co/v1/transaction/initialize",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                chapa_response = response.json()
                
                if chapa_response.get('status') == 'success':
                    checkout_url = chapa_response.get('data', {}).get('checkout_url')
                    
                    chapa_tx_id = chapa_response.get('data', {}).get('tx_ref')
                    if chapa_tx_id:
                        payment.chapa_transaction_id = chapa_tx_id
                        payment.save()
                    
                    return Response({
                        'payment_id': payment.id,
                        'checkout_url': checkout_url,
                        'tx_ref': tx_ref,
                        'amount': amount
                    }, status=status.HTTP_200_OK)
                else:
                    payment.status = 'failed'
                    payment.save()
                    return Response({
                        'error': 'Payment initialization failed',
                        'message': chapa_response.get('message', 'Unknown error')
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                payment.status = 'failed'
                payment.save()
                return Response({
                    'error': 'Payment initialization failed',
                    'message': 'Failed to communicate with payment gateway'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': 'Internal server error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerificationView(APIView):
    """
    Verify payment status with Chapa
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            tx_ref = request.data.get('tx_ref')
            
            if not tx_ref:
                return Response({
                    'error': 'tx_ref is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                payment = Payment.objects.get(
                    transaction_id__icontains=tx_ref.replace('CHAPA-', ''),
                    booking__user=request.user
                )
            except Payment.DoesNotExist:
                return Response({
                    'error': 'Payment not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"https://api.chapa.co/v1/transaction/verify/{tx_ref}",
                headers=headers
            )
            
            if response.status_code == 200:
                chapa_response = response.json()
                
                if chapa_response.get('status') == 'success':
                    chapa_data = chapa_response.get('data', {})
                    chapa_status = chapa_data.get('status')
                    
                    if chapa_status == 'success':
                        payment.status = 'completed'
                    elif chapa_status == 'failed':
                        payment.status = 'failed'
                    else:
                        payment.status = 'pending'
                    
                    payment.save()
                    
                    return Response({
                        'payment_id': payment.id,
                        'status': payment.status,
                        'amount': payment.amount,
                        'chapa_status': chapa_status
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': 'Verification failed',
                        'message': chapa_response.get('message', 'Unknown error')
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'Verification failed',
                    'message': 'Failed to communicate with payment gateway'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': 'Internal server error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentListView(generics.ListAPIView):
    """
    List payments for the current user
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(booking__user=self.request.user)


class PaymentDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific payment
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Payment.objects.filter(booking__user=self.request.user)