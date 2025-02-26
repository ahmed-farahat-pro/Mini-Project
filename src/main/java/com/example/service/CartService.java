package com.example.service;

import com.example.model.Cart;
import com.example.model.Product;
import com.example.repository.CartRepository;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.UUID;

@Service
public class CartService extends  MainService<Cart> {

    private final CartRepository cartRepository;

    // Constructor-based Dependency Injection
    public CartService(CartRepository cartRepository) {
        this.cartRepository = cartRepository;
    }

    public ArrayList<Cart> getCarts() {
        return cartRepository.getCarts();
    }

    public Cart getCartById(UUID cartId){
        return cartRepository.getCartById(cartId);
    }

    public Cart getCartByUserId(UUID userId) {
        return cartRepository.getCartByUserId(userId);
    }

    public Cart addCart(Cart cart) {
        return cartRepository.addCart(cart);
    }

    public void deleteCartById(UUID cartId) {
         cartRepository.deleteCart(cartId);
    }

    public boolean updateCart(Cart cart) {
        return cartRepository.updateCart(cart);
    }

    // Add a product to a user's cart
    public void addProductToCart(UUID userId, Product product) {
        Cart cart = cartRepository.getCartByUserId(userId);
        if (cart != null) {
            cart.addProduct(product);
            cartRepository.updateCart(cart);

        }else{
            cart = new Cart(userId, new ArrayList<>());
            cart.addProduct(product);
            cartRepository.addCart(cart); // Save the new cart

        }

    }

    // Remove a product from a user's cart
    public void deleteProductFromCart(UUID userId, Product product) {
        Cart cart = cartRepository.getCartByUserId(userId);
        if (cart != null) {
             cart.removeProduct(product);
            cartRepository.updateCart(cart);

        }


    }
}
