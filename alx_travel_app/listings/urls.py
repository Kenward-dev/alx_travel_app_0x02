from django.urls import path
from . import views

urlpatterns = [
    path('listings/', views.ListingListView.as_view(), name='listing-list'),
    path('listings/<int:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),
    
    path('bookings/', views.BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<int:id>/', views.BookingDetailView.as_view(), name='booking-detail'),
    
    path('reviews/', views.ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    
    path('payments/', views.PaymentListView.as_view(), name='payment-list'),
    path('payments/<int:id>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/initiate/', views.InitiatePaymentView.as_view(), name='payment-initiate'),
    path('payments/verify/', views.PaymentVerificationView.as_view(), name='payment-verify'),
]