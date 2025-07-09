from django.urls import path
from . import views

urlpatterns = [
    # User URLs
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/create/', views.UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    
    # Dish URLs
    path('dishes/', views.DishListView.as_view(), name='dish-list'),
    # ... other dish URLs ...
    
    # Order URLs
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    # ... other order URLs ...
    
    # OrderItem URLs
    path('order-items/create/', views.OrderItemCreateView.as_view(), name='order-item-create'),
    # ... other order item URLs ...
]