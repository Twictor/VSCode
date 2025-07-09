from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import User, Dish, Order, OrderItem

# User Views
class UserListView(ListView):
    model = User
    template_name = 'users/list.html'
    context_object_name = 'users'

class UserDetailView(DetailView):
    model = User
    template_name = 'users/detail.html'

class UserCreateView(CreateView):
    model = User
    template_name = 'users/create.html'
    fields = ['name', 'phone', 'role']
    success_url = reverse_lazy('user-list')

class UserUpdateView(UpdateView):
    model = User
    template_name = 'users/update.html'
    fields = ['name', 'phone', 'role']
    
    def get_success_url(self):
        return reverse_lazy('user-detail', kwargs={'pk': self.object.pk})

class UserDeleteView(DeleteView):
    model = User
    template_name = 'users/delete.html'
    success_url = reverse_lazy('user-list')

# Dish Views (similar pattern)
class DishListView(ListView):
    model = Dish
    template_name = 'dishes/list.html'
    context_object_name = 'dishes'

# ... other Dish CRUD views ...

# Order Views
class OrderListView(ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

class OrderCreateView(CreateView):
    model = Order
    template_name = 'orders/create.html'
    fields = ['user', 'status']
    success_url = reverse_lazy('order-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Here you can add logic to create order items
        return response

# ... other Order CRUD views ...

# OrderItem Views
class OrderItemCreateView(CreateView):
    model = OrderItem
    template_name = 'order_items/create.html'
    fields = ['order', 'dish', 'quantity']
    
    def form_valid(self, form):
        # Set price_at_order to current dish price
        form.instance.price_at_order = form.instance.dish.price
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('order-detail', kwargs={'pk': self.object.order.pk})

# ... other OrderItem CRUD views ...