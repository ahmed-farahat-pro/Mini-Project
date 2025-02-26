package com.example.service;

import com.example.model.Cart;
import com.example.model.Order;
import com.example.model.Product;
import com.example.model.User;
import com.example.repository.CartRepository;
import com.example.repository.UserRepository;
import com.example.repository.OrderRepository;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
public class UserService extends  MainService<User>{
    private final CartService cartService  ;
    private final UserRepository userRepository;
    private final CartRepository cartRepository;
    private final OrderRepository orderRepository;

    // Constructor-based Dependency Injection
    public UserService(CartService cartService, UserRepository userRepository, CartRepository cartRepository, OrderRepository orderRepository) {
        this.cartService = cartService;
        this.userRepository = userRepository;
        this.cartRepository = cartRepository;
        this.orderRepository = orderRepository;
    }

    // Get all users
    public ArrayList<User> getUsers() {
        return userRepository.getUsers();
    }

    // Get user by ID
    public User getUserById(UUID userId) {
        return userRepository.getUserById(userId);
    }

    // Add a new user
    public User addUser(User user) {
        return userRepository.addUser(user);
    }

    // Delete a user
    public void deleteUser(UUID id) {
        userRepository.deleteUserById(id);
    }

    // Get all orders for a specific user
    public List<Order> getOrdersByUserId(UUID userId) {
        return userRepository.getOrdersByUserId(userId);
    }

    // Checkout: Convert cart to order and associate it with the user
    public void addOrderToUser(UUID userId) {
        // Get the user's cart
        Cart cart = cartRepository.getCartByUserId(userId);

        if (cart == null || cart.getProducts().isEmpty()) {
            throw new IllegalStateException("Cart is empty or does not exist.");
        }

        // Create a new order from cart items
        Order order = new Order();
        order.setProducts(new ArrayList<>(cart.getProducts())); // Copy cart items
        order.setTotalPrice(cart.calculateTotalPrice()); // Assume a method to calculate total price
        order.setUserId(userId);

        // Save the order in OrderRepository
        orderRepository.addOrder(order);

        // Add order to the user's order history
        userRepository.addOrderToUser(userId, order);

        // Clear the cart after checkout
        cart.getProducts().clear();
        cartRepository.updateCart(cart);
    }

    public void emptyCart(UUID userId) {
        Cart cart = cartService.getCartByUserId(userId); // Fetch cart using CartService

        if (cart == null || cart.getProducts().isEmpty()) {
            return; // No action needed if the cart is empty
        }

        // Remove each product one by one using removeProductFromCart()
        for (Product product : List.copyOf(cart.getProducts())) { // Avoid ConcurrentModificationException
            cartService.deleteProductFromCart(userId, product);
        }
    }
    public void removeOrderFromUser(UUID userId, UUID orderId)
    {
        userRepository.removeOrderFromUser(userId,  orderId);
    }
    public void deleteUserById(UUID userId){
        userRepository.deleteUserById(userId);
    }
}
